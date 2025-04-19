import streamlit as st
import cv2
import time
import qrcode
from io import BytesIO
from datetime import datetime
from PIL import Image
from ultralytics import YOLO
from twilio.rest import Client

# ─── Page & Style Setup ───────────────────────────────────────────────────────
st.set_page_config(page_title="Smart Billing System 💳",
                   page_icon="🛍️", layout="centered")

st.markdown("""
    <style>
    .stButton > button {
        background-color: #2ecc71;
        color: white;
        padding: 0.6em 1.2em;
        font-size: 1em;
        border-radius: 8px;
        margin: 5px;
    }
    .stButton > button:hover {
        background-color: #27ae60;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #2e9aff;'>
        🧾 Smart Billing System
    </h1>
   
    <hr style="border-top: 1px solid #bbb;">
""", unsafe_allow_html=True)

# ─── Load Model & Config ───────────────────────────────────────────────────────
model = YOLO("runs/detect/train/weights/best.pt")

TWILIO_SID = "AC337308f3f5e267c8fe9c8f857fab95ec"
TWILIO_AUTH_TOKEN = "4fae44e049033f5c4b89c40895ee4708"
TWILIO_PHONE_NUMBER = "+16672880864"

item_prices = {
    "milo-180ml": 20,
    "slice-200ml": 25,
    "lays-large": 50
}

# ─── Session State Initialization ─────────────────────────────────────────────
if 'detected_items' not in st.session_state:
    st.session_state.detected_items = {}
if 'scanning' not in st.session_state:
    st.session_state.scanning = False
if 'stopped' not in st.session_state:
    st.session_state.stopped = False
if 'phone_entered' not in st.session_state:
    st.session_state.phone_entered = False
if 'phone_number' not in st.session_state:
    st.session_state.phone_number = ""
if 'start_new_bill' not in st.session_state:
    st.session_state.start_new_bill = False

# ─── Reset Flow for New Bill ─────────────────────────────────────────────────
if st.session_state.start_new_bill:
    st.session_state.phone_entered = False
    st.session_state.phone_number = ""
    st.session_state.detected_items = {}
    st.session_state.scanning = False
    st.session_state.stopped = False
    st.session_state.start_new_bill = False
    st.rerun()

# ─── Phone Entry Screen ───────────────────────────────────────────────────────
if not st.session_state.phone_entered:
    st.title("📲 Welcome to Smart Billing")
    st.session_state.phone_number = st.text_input(
        "Enter your mobile number:", max_chars=10, key="phone_input"
    )
    if st.button("Proceed"):
        if len(st.session_state.phone_number) == 10 and st.session_state.phone_number.isdigit():
            st.session_state.phone_entered = True
        else:
            st.warning("⚠️ Please enter a valid 10-digit mobile number.")
    st.stop()

# Main Billing UI
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📸 Start Scanning"):
        st.session_state.scanning = True
        st.session_state.stopped = False
        st.session_state.detected_items = {}
with col2:
    if st.button("🔄 Reset"):
        st.session_state.detected_items = {}
        st.session_state.stopped = False
with col3:
    if st.button("⛔ Stop"):
        st.session_state.scanning = False
        st.session_state.stopped = True

bill_placeholder = st.empty()

def display_bill(editable=False):
    total = 0
    with bill_placeholder.container():
        st.markdown("### 🛍️ Current Bill")
        for item, count in st.session_state.detected_items.copy().items():
            price = item_prices.get(item, 0)
            subtotal = price * count
            total += subtotal

            cols = st.columns([3, 1, 1])
            cols[0].markdown(f"**{item}** - ₹{price} × {count} = ₹{subtotal}")
            if editable:
                if cols[1].button("➕", key=f"plus_{item}"):
                    st.session_state.detected_items[item] += 1
                if cols[2].button("➖", key=f"minus_{item}"):
                    if st.session_state.detected_items[item] > 1:
                        st.session_state.detected_items[item] -= 1
                    else:
                        del st.session_state.detected_items[item]
        st.markdown(f"### 💰 Total: ₹{total}")
    return total

# ─── Detection Loop ───────────────────────────────────────────────────────────
if st.session_state.scanning:
    cap = cv2.VideoCapture(0)
    stframe = st.empty()
    while st.session_state.scanning:
        ret, frame = cap.read()
        if not ret:
            st.error("⚠️ Cannot access camera.")
            break
        results = model.predict(frame, conf=0.5)[0]
        names = model.names
        for box in results.boxes.data.tolist():
            cls_name = names[int(box[5])]
            if cls_name not in st.session_state.detected_items:
                st.session_state.detected_items[cls_name] = 1
        annotated = results.plot()
        stframe.image(annotated, channels="BGR")
        display_bill()
        time.sleep(0.2)
    cap.release()

# ─── Final Bill & SMS Sending ────────────────────────────────────────────────
if st.session_state.stopped and st.session_state.detected_items:
    st.markdown("---")
    st.markdown("## ✅ Final Bill")
    total = display_bill(editable=True)

    if st.button("Next ➡️ Send Invoice"):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build SMS body
        msg_body = (
            f"Bill Invoice date: {current_time}\n"
            "Thank you for shopping with us\n"
            "Items:\n"
        )
        for item, count in st.session_state.detected_items.items():
            msg_body += f"{item} - {count} pcs\n"
        msg_body += f"Total: ₹{total}"

        # Send via Twilio
        with st.spinner("📤 Sending invoice..."):
            try:
                client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
                to_number = "+91" + st.session_state.phone_number
                client.messages.create(
                    body=msg_body,
                    from_=TWILIO_PHONE_NUMBER,
                    to=to_number
                )
                st.success("✅ Message sent!")
            except Exception:
                st.error("❌ Message failed to send. Check Twilio console.")

    # ── Start New Bill ─────────────────────────────────────────────────────────
    if st.button("🧾 Start New Bill"):
        st.session_state.start_new_bill = True
        st.rerun()

# ─── Footer with Links & QR ──────────────────────────────────────────────────
linkedin_url = "https://www.linkedin.com/in/pawan-bhatia-5a119b274/"
github_url   = "https://github.com/pawanbhatia1304/Smart_Billing_AI"
email_addr   = "smartbillingai@gmail.com"

# Generate QR
qr = qrcode.make(github_url)
buf = BytesIO()
qr.save(buf, format="PNG")
buf.seek(0)
qr_img = Image.open(buf)

st.markdown("<hr>", unsafe_allow_html=True)
cols = st.columns([2,1,2])
with cols[0]:
    st.image(qr_img, width=100, caption="Smart Billing Github")
with cols[1]:
    st.markdown(f"""
        <div style='text-align:center; color:white; font-size:0.9em;'>
            <strong>TrendBots</strong><br>
            <a href="{linkedin_url}" target="_blank">LinkedIn</a> |
            <a href="{github_url}" target="_blank">GitHub</a><br>
            {email_addr}
        </div>
    """, unsafe_allow_html=True)
with cols[2]:
    st.write("")  # spacer
