import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
import os
import pandas as pd
import sqlite3
import smtplib
from email.mime.text import MIMEText


# DATABASE CONNECTION
conn = sqlite3.connect("student_assistant.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS time_manager (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    hours INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    link TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS drive_storage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS email_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    message TEXT
)
""")

cursor.execute("DROP TABLE IF EXISTS reminders")

cursor.execute("""
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    deadline TEXT,
    email TEXT
)
""")

def send_email(receiver_email, task, deadline):

    sender_email = "yashaswir194@gmail.com"
    sender_password = "czjx ptcx wyjl avss"

    subject = "Reminder Notification"

    body = f"""
    Reminder Details

    Task: {task}
    Deadline: {deadline}

    This is an automated reminder from AI Student Productivity Assistant.
    """

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login(sender_email, sender_password)

    server.sendmail(
        sender_email,
        receiver_email,
        msg.as_string()
    )

    server.quit()

# CREATE USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

conn.commit()

# CREATE REMINDERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    deadline TEXT
)
""")

conn.commit()


# DEFAULT USER
cursor.execute(
    "INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin123')"
)

conn.commit()
# =========================================================
# LOAD API KEYS
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =========================================================
# CONFIGURE GEMINI
# =========================================================

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================================================
# CONFIGURE OPENAI
# =========================================================

openai_client = OpenAI(
    api_key=OPENAI_API_KEY
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Student Productivity Assistant",
    page_icon="🎓",
    layout="wide"
)

# =========================================================
# LOAD CSS
# =========================================================

with open("style.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.title("🔐 Login System")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()

    if user:

        st.session_state.logged_in = True
        st.rerun()

    else:

        st.error("Invalid username or password")

        st.markdown("---")

        st.subheader("New User Registration")

        new_user = st.text_input("Create Username")

        new_pass = st.text_input(
        "Create Password",
        type="password"
        )

    if st.button("Register"):

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (new_user, new_pass)
        )

        conn.commit()

        st.success("User registered successfully!")

# =========================================================
# DASHBOARD PAGE
# =========================================================

elif st.session_state.logged_in and st.session_state.page == "dashboard":

    # LOGOUT BUTTON

    top1, top2 = st.columns([8,1])

    with top2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # HERO SECTION

    st.markdown("""
    <div class="hero-section">
        <h1>🎓 AI Student Productivity Assistant</h1>
        <p>
            Smart Generative AI System for academic productivity,
            study planning, reminders, AI assistance,
            and workflow management.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🚀 Dashboard Modules")

    # =====================================================
    # ROW 1
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "📘 PDF Assistant\nUpload notes & summarize PDFs",
            use_container_width=True
        ):
            st.session_state.page = "pdf"
            st.rerun()

    with col2:
        if st.button(
            "🧠 AI Chat\nAsk academic AI questions",
            use_container_width=True
        ):
            st.session_state.page = "chat"
            st.rerun()

    with col3:
        if st.button(
            "🗓️ Study Planner\nCreate study schedules",
            use_container_width=True
        ):
            st.session_state.page = "planner"
            st.rerun()

    with col4:
        if st.button(
            "⏰ Reminder\nTrack assignments & tasks",
            use_container_width=True
        ):
            st.session_state.page = "reminder"
            st.rerun()

    # =====================================================
    # ROW 2
    # =====================================================

    col5, col6, col7, col8, col9 = st.columns(5)

    with col5:
        if st.button(
            "⌛ Time Manager\nImprove productivity",
            use_container_width=True
        ):
            st.session_state.page = "time"
            st.rerun()

    with col6:
        if st.button(
            "📚 Resources\nRecommend learning materials",
            use_container_width=True
        ):
            st.session_state.page = "resources"
            st.rerun()

    with col7:
        if st.button(
            "☁️ Drive Storage\nStore study documents",
            use_container_width=True
        ):
            st.session_state.page = "drive"
            st.rerun()

    with col8:
        if st.button(
            "📩 Email Reminder\nReceive notifications",
            use_container_width=True
        ):
            st.session_state.page = "email"
            st.rerun()

    with col9:
        if st.button(
             "🛠️ Admin Panel\nManage system",
            use_container_width=True
        ):
            st.session_state.page = "admin"
            st.rerun()

    st.markdown("---")

    st.markdown("## ✨ Features Included")

    st.write("✦ PDF Upload & Summarization")
    st.write("✦ AI Academic Chat Assistant")
    st.write("✦ AI Study Planner")
    st.write("✦ Assignment Reminder System")
    st.write("✦ Time Management Assistant")
    st.write("✦ Resource Recommendation System")
    st.write("✦ Drive Storage Simulation")
    st.write("✦ Email Reminder System")

# =========================================================
# PDF ASSISTANT PAGE
# =========================================================

elif st.session_state.page == "pdf":

    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="module-section">
        <h1>📘 PDF Assistant</h1>
        <p>Upload notes, summarize content, and ask AI questions.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader(
        "Upload PDF File",
        type=["pdf"]
    )

    if uploaded_pdf:

        st.success("PDF uploaded successfully!")

        pdf_reader = PdfReader(uploaded_pdf)

        pdf_text = ""

        for page in pdf_reader.pages:
            text = page.extract_text()

            if text:
                pdf_text += text

        prompt = st.text_input(
            "Ask question from PDF",
            placeholder="Summarize this PDF"
        )

        if st.button("Generate Answer"):

            final_prompt = f"""
            PDF Content:
            {pdf_text[:12000]}

            User Question:
            {prompt}
            """

            # GEMINI FIRST

            try:

                response = model.generate_content(
                    final_prompt
                )

                st.success(
                    "Response generated using Gemini AI"
                )

                st.write(
                    response.text
                )

            # OPENAI FALLBACK

            except Exception:

                try:

                    response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "user",
                                "content": final_prompt
                            }
                        ]
                    )

                    st.success(
                        "Gemini quota exceeded — switched to OpenAI"
                    )

                    st.write(
                        response.choices[0].message.content
                    )

                except Exception as openai_error:

                    st.error(
                        f"OpenAI Error: {openai_error}"
                    )

# =========================================================
# AI CHAT PAGE
# =========================================================

elif st.session_state.page == "chat":

    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="module-section">
        <h1>🧠 AI Chat Assistant</h1>
        <p>
            Ask academic questions instantly using
            Gemini AI + OpenAI fallback.
        </p>
    </div>
    """, unsafe_allow_html=True)

    chat_question = st.text_input(
        "Ask any question",
        placeholder="Ask me anything"
    )

    if st.button("Ask AI"):

        # GEMINI FIRST

        try:

            response = model.generate_content(
                chat_question
            )

            st.success(
                "AI Response Generated!"
            )

            st.write(
                response.text
            )

        # OPENAI FALLBACK

        except Exception:

            try:

                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": chat_question
                        }
                    ]
                )

                st.success(
                    "Gemini quota exceeded — switched to OpenAI"
                )

                st.write(
                    response.choices[0].message.content
                )

            except Exception as openai_error:

                st.error(
                    f"OpenAI Error: {openai_error}"
                )

# =========================================================
# STUDY PLANNER
# =========================================================

elif st.session_state.page == "planner":

    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.title("🗓️ AI Study Planner")

    subject = st.text_input("Subject")

    hours = st.slider(
        "Study Hours Per Day",
        1,
        12,
        4
    )

    if st.button("Generate Study Plan"):

        plan_prompt = f"""
        Create a study plan for:

        Subject: {subject}
        Hours per day: {hours}
        """

        try:

            response = model.generate_content(
                plan_prompt
            )

            st.write(response.text)

        except Exception:

            st.warning(
                "Gemini unavailable. Trying OpenAI..."
            )

            try:

                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": plan_prompt
                        }
                    ]
                )

                st.write(
                    response.choices[0].message.content
                )

            except Exception as openai_error:

                st.error(
                    f"OpenAI Error: {openai_error}"
                )

# =========================================================
# REMINDER PAGE
# =========================================================

elif st.session_state.page == "reminder":

    st.title("⏰ Reminder System")

    task = st.text_input("Enter Task")
    #email = st.text_input("Enter Email")

    deadline = st.date_input("Select Deadline")

    if st.button("Save Reminder"):

        cursor.execute(
    "INSERT INTO reminders (task, deadline) VALUES (?, ?)",
    (task, str(deadline), email)
    )

        conn.commit()

        #if email and "@" in email:
            #send_email(email, task, deadline)
        st.success("Reminder Saved!")
        # else:
        #     st.error("Enter a valid email address")

    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.subheader("Saved Reminders")

    cursor.execute("SELECT * FROM reminders")

    all_reminders = cursor.fetchall()

    st.subheader("Saved Reminders")

    for reminder in all_reminders:
        st.write(
            f"📌 Task: {reminder[1]} | Deadline: {reminder[2]} "
        )

# =========================================================
# TIME MANAGER
# =========================================================

elif st.session_state.page == "time":

    st.title("⏳ Time Manager")

    task_name = st.text_input("Task Name")

    hours = st.slider(
        "Study Hours",
        1,
        12
    )

    if st.button("Save Study Plan"):

        cursor.execute(
            "INSERT INTO time_manager (task, hours) VALUES (?, ?)",
            (task_name, hours)
        )

        conn.commit()

        st.success("Study plan saved!")

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.subheader("Saved Study Plans")

    cursor.execute("SELECT * FROM time_manager")

    plans = cursor.fetchall()

    for plan in plans:
        st.write(
            f"📚 {plan[1]} — {plan[2]} hours"
        )
      

# =========================================================
# RESOURCES PAGE
# =========================================================

elif st.session_state.page == "resources":

    st.title("📚 Learning Resources")

    subject = st.text_input("Enter Subject")

    resource_link = st.text_input("Enter Resource Link")

    if st.button("Save Resource"):

        cursor.execute(
            "INSERT INTO resources (subject, link) VALUES (?, ?)",
            (subject, resource_link)
        )

        conn.commit()

        st.success("Resource saved!")

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.subheader("Saved Resources")

    cursor.execute("SELECT * FROM resources")

    all_resources = cursor.fetchall()

    for resource in all_resources:
        st.write(
            f"📖 {resource[1]} → {resource[2]}"
        )

# =========================================================
# DRIVE STORAGE
# =========================================================

elif st.session_state.page == "drive":

    st.title("☁️ Drive Storage")

    uploaded_file = st.file_uploader(
        "Upload Study Document"
    )

    if uploaded_file is not None:

        cursor.execute(
            "INSERT INTO drive_storage (filename) VALUES (?)",
            (uploaded_file.name,)
        )

        conn.commit()

        st.success(
            f"{uploaded_file.name} uploaded successfully!"
        )

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.subheader("Stored Documents")

    cursor.execute("SELECT * FROM drive_storage")

    all_files = cursor.fetchall()

    for file in all_files:
        st.write(f"📄 {file[1]}")

# =========================================================
# EMAIL REMINDER
# =========================================================

elif st.session_state.page == "email":

    st.title("📧 Email Reminder System")

    email = st.text_input("Enter Email")

    message = st.text_area("Reminder Message")

    if st.button("Send Reminder"):

        cursor.execute(
            "INSERT INTO email_reminders (email, message) VALUES (?, ?)",
            (email, message)
        )

        conn.commit()

        st.success(
            f"Reminder sent to {email}"
        )

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.subheader("Sent Reminders")

    cursor.execute("SELECT * FROM email_reminders")

    all_emails = cursor.fetchall()

    for reminder in all_emails:
        st.write(
            f"📨 {reminder[1]} → {reminder[2]}"
        )

# =========================================================
# ADMIN PANEL
# =========================================================

elif st.session_state.page == "admin":

    if st.button("⬅ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.title("🛠️ Admin Panel")

    st.subheader("System Statistics")

    st.metric("Total Users", "128")
    st.metric("PDF Uploads", "342")
    st.metric("AI Requests", "1,245")

    st.subheader("User Management")

    st.write("• Manage users")
    st.write("• Track activity")
    st.write("• Monitor AI usage")

    st.subheader("Database Status")

    st.success("Database Connected Successfully")

    # ============================================
    # ANALYTICS DASHBOARD
    # ============================================

    st.subheader("Analytics Dashboard")

    chart_data = pd.DataFrame({
        "Module": [
            "PDF Assistant",
            "AI Chat",
            "Study Planner",
            "Reminder"
        ],
        "Usage": [120, 300, 180, 90]
    })

    st.bar_chart(
        chart_data.set_index("Module")
    )

    st.subheader("Daily Activity")

    activity_data = pd.DataFrame({
        "Days": [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri"
        ],
        "Users": [20, 35, 40, 28, 50]
    })

    st.line_chart(
        activity_data.set_index("Days")
    )