import subprocess
import os
import gradio as gr
import requests
import json
import mysql.connector
from datetime import datetime

OLLAMA_SERVER_URL = "http://localhost:11434"

# ------------------ LLM ------------------
def summarize_with_model(context: str, text: str) -> str:
    llm_model_name = "llama3.2:latest"

    prompt = f"""
You are a professional meeting assistant.

Provide:
1. Summary
2. Key Points
3. Action Items

Context:
{context if context else 'No context'}

Transcript:
{text}
"""

    response = requests.post(
        f"{OLLAMA_SERVER_URL}/api/generate",
        json={"model": llm_model_name, "prompt": prompt},
        stream=True,
        timeout=60
    )

    full_response = ""

    for line in response.iter_lines():
        if line:
            json_line = json.loads(line.decode("utf-8"))

            full_response += json_line.get(
                "response",
                ""
            )

            if json_line.get("done", False):
                break

    return full_response


# ------------------ AUDIO ------------------
def preprocess_audio_file(audio_file_path: str) -> str:

    output_wav_file = (
        f"{os.path.splitext(audio_file_path)[0]}_converted.wav"
    )

    cmd = (
        f'ffmpeg -y -i "{audio_file_path}" '
        f'-ar 16000 -ac 1 "{output_wav_file}"'
    )

    subprocess.run(
        cmd,
        shell=True,
        check=True
    )

    return output_wav_file


# ------------------ DB ------------------
def save_to_db(filename, summary, transcript):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="system",
        database="meeting_db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO meetings
        (filename, summary, transcript)
        VALUES (%s, %s, %s)
        """,
        (filename, summary, transcript)
    )

    conn.commit()
    conn.close()


# ------------------ HISTORY ------------------
def get_history_list():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="system",
        database="meeting_db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, filename FROM meetings ORDER BY id DESC"
    )

    rows = cursor.fetchall()

    conn.close()

    return gr.update(
        choices=[
            (f"{r[1]} (ID: {r[0]})", r[0])
            for r in rows
        ],
        visible=True
    )


def get_meeting_details(meeting_id):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="system",
        database="meeting_db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT summary, transcript
        FROM meetings
        WHERE id=%s
        """,
        (meeting_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row if row else (
        "No summary",
        "No transcript"
    )


# ------------------ MAIN ------------------
def process_audio(audio_file_path, context):

    if not audio_file_path:
        return "Upload or record audio first", ""

    # TIMESTAMP
    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    original_name = os.path.basename(
        audio_file_path
    )

    # CHECK RECORDED OR UPLOADED
    if original_name.startswith("audio"):
        new_filename = (
            f"{timestamp}_recorded.wav"
        )
    else:
        new_filename = (
            f"{timestamp}_{original_name}"
        )

    new_path = os.path.join(
        os.path.dirname(audio_file_path),
        new_filename
    )

    os.rename(
        audio_file_path,
        new_path
    )

    # AUDIO PREPROCESSING
    audio_file_wav = preprocess_audio_file(
        new_path
    )

    output_name = os.path.splitext(
        new_path
    )[0]

    # WHISPER TRANSCRIPTION
    subprocess.run([
        "whisper.cpp\\Release\\whisper-cli.exe",
        "-m",
        "whisper.cpp\\models\\ggml-base.bin",
        audio_file_wav,
        "-otxt",
        "-of",
        output_name,
        "-nt"
    ], check=True)

    # READ TRANSCRIPT
    with open(
        f"{output_name}.txt",
        "r",
        encoding="utf-8"
    ) as f:

        transcript = f.read()

    # GENERATE SUMMARY
    summary = summarize_with_model(
        context,
        transcript
    )

    # SAVE TO DB
    save_to_db(
        new_filename,
        summary,
        transcript
    )

    return summary, transcript


# ------------------ UI ------------------
with gr.Blocks(css="""
#submit_btn, #history_btn {
    background-color: orange !important;
    color: white !important;
    font-weight: bold;
}

.copy_icon {
    min-width: 32px !important;
    background: white !important;
    border: none !important;
    font-size: 16px !important;
    cursor: pointer;
}

.copy_icon:hover {
    background: #f2f2f2 !important;
    border-radius: 6px;
}

.download_btn {
    background-color: orange !important;
    color: white !important;
    border-radius: 6px !important;
    padding: 6px 10px !important;
    font-size: 13px !important;
}
""") as iface:

    gr.Markdown(
        "## AI POWERED MEETING SUMMARIZER"
    )

    with gr.Row():

        # LEFT SIDE
        with gr.Column():

            audio_input = gr.Audio(
                type="filepath",
                label="Audio"
            )

            context_input = gr.Textbox(
                label="Context"
            )

            submit_btn = gr.Button(
                "Submit",
                elem_id="submit_btn"
            )

            history_btn = gr.Button(
                "View History",
                elem_id="history_btn"
            )

            history_dropdown = gr.Dropdown(
                label="Select Meeting",
                choices=[],
                visible=False
            )

        # RIGHT SIDE
        with gr.Column():

            # SUMMARY
            with gr.Group():

                with gr.Row():

                    gr.Markdown("## Summary")

                    copy_summary_btn = gr.Button(
                        "Copy",
                        elem_classes="copy_icon"
                    )

                summary_output = gr.Textbox(
                    lines=5,
                    max_lines=5
                )

                download_summary_btn = gr.Button(
                    "⬇ Download Summary",
                    elem_classes="download_btn"
                )

            # TRANSCRIPT
            with gr.Group():

                with gr.Row():

                    gr.Markdown("## Transcript")

                    copy_transcript_btn = gr.Button(
                        "Copy",
                        elem_classes="copy_icon"
                    )

                transcript_output = gr.Textbox(
                    lines=5,
                    max_lines=5
                )

                download_transcript_btn = gr.Button(
                    "⬇ Download Transcript",
                    elem_classes="download_btn"
                )

    # ---------------- ACTIONS ----------------

    # PROCESS AUDIO
    submit_btn.click(
        process_audio,
        inputs=[
            audio_input,
            context_input
        ],
        outputs=[
            summary_output,
            transcript_output
        ]
    )

    # VIEW HISTORY
    history_btn.click(
        get_history_list,
        outputs=history_dropdown
    )

    # LOAD HISTORY ITEM
    history_dropdown.change(
        get_meeting_details,
        inputs=history_dropdown,
        outputs=[
            summary_output,
            transcript_output
        ]
    )

    # COPY SUMMARY
    copy_summary_btn.click(
        None,
        inputs=[summary_output],
        outputs=[],
        js="""
        (text) => {
            navigator.clipboard.writeText(text);
        }
        """
    )

    # COPY TRANSCRIPT
    copy_transcript_btn.click(
        None,
        inputs=[transcript_output],
        outputs=[],
        js="""
        (text) => {
            navigator.clipboard.writeText(text);
        }
        """
    )

    # DOWNLOAD SUMMARY
    download_summary_btn.click(
        None,
        inputs=[summary_output],
        outputs=[],
        js="""
        (text) => {

            const blob = new Blob(
                [text],
                { type: "text/plain" }
            );

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");

            a.href = url;
            a.download = "summary.txt";

            a.click();

            window.URL.revokeObjectURL(url);
        }
        """
    )

    # DOWNLOAD TRANSCRIPT
    download_transcript_btn.click(
        None,
        inputs=[transcript_output],
        outputs=[],
        js="""
        (text) => {

            const blob = new Blob(
                [text],
                { type: "text/plain" }
            );

            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");

            a.href = url;
            a.download = "transcript.txt";

            a.click();

            window.URL.revokeObjectURL(url);
        }
        """
    )


# ---------------- LAUNCH ----------------
iface.launch(debug=True)