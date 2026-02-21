from telegram import InlineKeyboardButton, InlineKeyboardMarkup 
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from pathlib import Path
from dotenv import load_dotenv
import os
import csv
import datetime


# Holds Telegram file_ids for subsequent sends
FILE_IDS = {}
# Holds raw bytes for first upload
FILE_CACHE = {}


THUMBNAILS = {
    "digital_access_steps_video": "./responses/thumbnails/Digital Access Thumbnail.jpeg",
    "blocked_customer_video": "./responses/thumbnails/unblocking on cbs.jpg",
    "Approve_of_Digital_Access_on_CBS_video": "./responses/thumbnails/cbs approval.jpg",
}

# ===== STORAGE LOGIC =====
def save_report_to_file(name, phone, issue):
    os.makedirs("reports", exist_ok=True)
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Map issue names to clean filenames
    if "Phone" in issue:
        filename = f"reports/Already_Existed_Phone_{current_date}.csv"
    elif "Blocked" in issue:
        filename = f"reports/Blocked_Users_{current_date}.csv"
    elif "Automatically Returning to Login Screen" in issue:
        filename = f"reports/Automatically_Returning_to_Login_Screen_{current_date}.csv"
    else:
        filename = f"reports/General_Issues_{current_date}.csv"
    
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    row = [timestamp, name, phone]
    file_exists = os.path.isfile(filename)
    
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Time", "Customer Name", "Phone Number"])
        writer.writerow(row)
    print(f"Logged to daily CSV: {filename}")



def load_files():
    files_to_load = {
        "digital_ambassador_pdf": "./responses/Designation of Tech-Native.pdf",
        "digital_access_steps_video": "./responses/Digital Access Steps.mp4",
        "blocked_customer_video": "./responses/videos/Unlocking and Unblocking customer.mp4",
        "Approve_of_Digital_Access_on_CBS_video": "./responses/videos/Approval of Digital Access on CBS (Manual Review).mp4",

    }

    for key, path_str in files_to_load.items():
        path = Path(path_str)
        if path.exists():
            FILE_CACHE[key] = path.read_bytes()
            print(f"Loaded {key} into memory")
        else:
            print(f"File not found: {path}")

load_files()
load_dotenv()



async def send_cached_file(update: Update, key: str, caption: str = "",parse_mode: str = None):
    """
    Sends a cached file (PDF, video, etc.) using Telegram file_id if available.
    """
    if key not in FILE_CACHE:
        await update.message.reply_text(f"File '{key}' not found in cache.")
        return

    # Determine if file is PDF or Video
    is_pdf = key.endswith("pdf")
    is_video = key.endswith("video") or key.endswith("mov")

    # First upload — store Telegram file_id
    if key not in FILE_IDS:
        if is_pdf:
            msg = await update.message.reply_document(
                document=FILE_CACHE[key],
                filename=f"{key}.pdf",
                caption=caption,
                parse_mode=parse_mode
            )
            FILE_IDS[key] = msg.document.file_id
        elif is_video:
            thumbnail_path = THUMBNAILS.get(key)
            if thumbnail_path and Path(thumbnail_path).exists():
                with open(thumbnail_path, "rb") as thumb:
                    msg = await update.message.reply_video(
                        video=FILE_CACHE[key],
                        caption=caption,
                        thumbnail=thumb,
                        supports_streaming=True,
                        parse_mode=parse_mode, 
            )
            else:
                msg = await update.message.reply_video(
                video=FILE_CACHE[key] if key not in FILE_IDS else FILE_IDS[key],
                caption=caption,
                supports_streaming=True,
                parse_mode=parse_mode,
        )
            FILE_IDS[key] = msg.video.file_id

        else:
            await update.message.reply_text("Unsupported file type.")
    else:
        # Reuse Telegram file_id — instant
        if is_pdf:
            await update.message.reply_document(
                document=FILE_IDS[key],
                caption=caption,
                parse_mode=parse_mode
            )
        elif is_video:
            await update.message.reply_video(
                video=FILE_IDS[key],
                caption=caption,
                supports_streaming=True,
                # thumbnail=open("./responses/thumbnails/Digital Access Thumbnail.jpeg", "rb"),
                parse_mode=parse_mode
            )
        else:
            await update.message.reply_text("Unsupported file type.")


# ===== BOT CONFIGURATION =====
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ===== SETUP LOGGING =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== KEYBOARD DEFINITION =====
def get_main_keyboard():
    """Create the main menu keyboard with all your menu items"""
    keyboard = [        
        # ["🔥🔥 IMMEDIATE ALERT (አስቸኳይ መረጃ) 🔥🔥"],
        ["Designation of Digital Ambassador at Branches"],
        ["❗️Announcements for Invalid Backoffice Requests"],
        ["Backoffice User Access Updates"],
        ["Digital Access Process"],
        ["Report Issue"],
        ["Digital Access Approval on CBS (Manual Review)"],
        ["How to unlock customer in the backoffice"],
        ["How to login to DBS backoffice"],
        ["What branches do when the customer is blocked"],
        ["ALREADY EXISTING PHONE NO"],
        ["How Anbesa Plus supports local language"],
        ["How to release trusted device"],
        ["How to search customer in DBS backoffice"],
        ["How Forgot password works"],
        ["⬇️ Download Anbesa Plus Application"],
        ["DBS End User Manual for Branches"],
        ["DBS Back Office / Portal User Access Request Form"],
        ["When OTP is not reaching to the customer's mobile"],
        ["Overlay Detected Avoid Entering Sensetive Information Error"],
        # ["Reported And Fixed Issues"],

    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_app_download_menu():
    keyboard = [
        ["Android App Download Link"],
        ["Iphone App Download Link"],
        ["🏠 Main Menu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Reported And Fixed Issues
def get_reported_and_fixed_issues_menu():
    keyboard = [
        ["Fixed Phone Number Already Exists Issues"],
        ["Fixed Blocked User/Account Issues"],
        ['"Fixed Automatically Returning to Login Screen Issues"'], 
        ["🏠 Main Menu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_issue_report_menu():
    keyboard = [
        ["Phone Number Already Exists"],
        ["Blocked User/Account"],
        ['"Automatically Returning to Login Screen"'], 
        ["🏠 Main Menu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)




# ===== COMMAND HANDLERS =====
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with clean formatting and redirect support"""
    # 1. Check if user came from the "Report" link in a group
    if context.args and "report" in context.args:
        await update.message.reply_text(
    "📝 *Issue Reporting Steps:*\n\n"
    "1️⃣ Select *Report Issue* from the main menu.\n"
    "2️⃣ Select the specific *Issue Type* below.\n"
    "3️⃣ Enter the customer's *Full Name*"
    "4️⃣ Enter the customer's *Phone Number*",
    reply_markup=get_issue_report_menu(),
    parse_mode="Markdown"
)
        return

    # 2. Welcome Message
    welcome_text = (
    "👋 **Welcome to AnbesaPlus Helper Bot!**\n\n"
    "This bot helps you resolve technical questions and report issues. "
    "Select an option from the menu below to begin."
)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
    logger.info(f"User {update.effective_user.id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """Available Commands:
/start - Show welcome message with keyboard
/help - Show this help message

Select an option from the keyboard below for specific help:"""
    
    await update.message.reply_text(
        help_text,
        reply_markup=get_main_keyboard()
    )
    return

# ===== BUTTON HANDLERS =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages, button clicks, and reporting states"""
    user_message = update.message.text
    # Get the current state
    state = context.user_data.get("state")

    # ==========================================
    # ZONE 1: PRIORITY COMMANDS & RESET BUTTONS
    # ==========================================
    # These always run first. If a user clicks a button, we stop any "recording".
    
    # if user_message == "🏠 Main Menu" or user_message == "🔙 Back":
    #     context.user_data.clear() # Reset everything
    #     await update.message.reply_text("Returning to Main menu...", reply_markup=get_main_keyboard())
    #     return
    if user_message == "Report Issue":
        # Check if the message is coming from a group
        if update.effective_chat.type in ["group", "supergroup"]:
            #  URL button to the bot's private chat The 'start=report' part acts as a deep link
            bot_username = (await context.bot.get_me()).username
            keyboard = [
                [InlineKeyboardButton("➡️ Start Reporting", url=f"https://t.me/{bot_username}?start=report")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
    "🛡️ *Privacy & Security Notice*\n\n"
    "To protect customer phone numbers and keep this group clean and organized, "
    "all reporting must be done in a *private chat* through the bot.\n\n"
    "የደንበኞችን መረጃ ለመጠበቅ እና ይህን Group ንፁህ እና የተደራጀ ለማድረግ ሁሉም ሪፖርት ከቦት ጋር በሚደረግ private chat መደረግ አለበት።\n\n"
    "Click the button below to start reporting.\n"
    "ሪፖርት ለማድረግ ከታች ያለውን Button ይጫኑ።",
    
    reply_markup=reply_markup,
    parse_mode="Markdown"
)
            return
        else:
            # If they are already in private chat, show the reporting menu
            context.user_data.clear()
            await update.message.reply_text("Select Issue Type:", reply_markup=get_issue_report_menu())
            return

    elif user_message == "Report Issue":
        context.user_data.clear() # Clear any old half-finished reports
        await update.message.reply_text("Select Issue Type:", reply_markup=get_issue_report_menu())
        return

    elif user_message == "Phone Number Already Exists":
        context.user_data["report_issue_type"] = "Phone Already Exists"
        context.user_data["state"] = "WAITING_FOR_NAME"
        await update.message.reply_text("*Existing Phone No Reporting...*", parse_mode="Markdown")
        await update.message.reply_text("Please enter the customer's **Full Name**:", parse_mode="Markdown")
        return

    elif user_message == "Blocked User/Account":
        context.user_data["report_issue_type"] = "User Blocked"
        context.user_data["state"] = "WAITING_FOR_NAME"
        await update.message.reply_text("*Account Blocked Reporting...*", parse_mode="Markdown")
        await update.message.reply_text("Please enter the customer's **Full Name**:", parse_mode="Markdown")
        return
# Automatically Returning to Login Screen
    elif user_message == '"Automatically Returning to Login Screen"':
        context.user_data["report_issue_type"] = "Automatically Returning to Login Screen"
        context.user_data["state"] = "WAITING_FOR_NAME"
        await update.message.reply_text("*Automatically Returning to Login Screen Reporting...*", parse_mode="Markdown")
        await update.message.reply_text("Please enter the customer's **Full Name**:", parse_mode="Markdown")
        return

    # ==========================================
    # ZONE 2: ACTIVE RECORDING (STATE MACHINE)
    # ==========================================
    # This logic only runs if the user is in the middle of a report.

    if state == "WAITING_FOR_NAME":
        context.user_data["temp_name"] = user_message
        context.user_data["state"] = "WAITING_FOR_PHONE"
        await update.message.reply_text(
            f"Full Name recorded:    {user_message}\n\nNow, please enter the **Phone Number**:", 
            parse_mode="Markdown"
        )
        return

    elif state == "WAITING_FOR_PHONE":
        name = context.user_data.get("temp_name")
        issue = context.user_data.get("report_issue_type")
        phone = user_message # This is what the user just typed
        
        # Save to your CSV file
        save_report_to_file(name, phone, issue)
        
        # CLEAR STATE so the next message doesn't trigger this again
        context.user_data.clear() 
        
        await update.message.reply_text(
            f"**Issue Reported Successfully**\n\n👤 **Full Name:**   {name}\n📱 **Phone:**   {phone}\n📝 **Type:**     {issue}",
            parse_mode="Markdown",
            reply_markup=get_issue_report_menu()
        )
        return


    
    # Digital Access Process
    if user_message == "Digital Access Process":
        response = """Digital Access Process
Video Tutorial: https://t.me/anbesaplus/2506
"""
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    
    # How to unlock customer in the backoffice
    elif user_message == "How to unlock customer in the backoffice":
        response = """Steps to unlock customer in the DBS Backoffice 
Video Tutorial: https://t.me/anbesaplus/2132
"""
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return

        # How to unlock customer in the backoffice
    elif user_message == "🔥🔥 IMMEDIATE ALERT (አስቸኳይ መረጃ) 🔥🔥":
        response = """
🔥* To make the rollout process of Anbesa Plus Smooth and Successful, we have arranged Second Round online session for all branches. Branches are expected to dedicate atleast one person for this session.*

*Digital Ambassadors of each branch must attend the session.*

*የአንበሳ ፕላስ መተግብሪያን እና የአንበሳ ባንክን የዲጅታል የለወጥ ሂደት የተሳካ እንዲሆን ለማድረግ ለሁሉም ቅርንጫፎች ሁለተኛ ዙር የኦላይን የጥያቄ እና መልስ ክፍለ ጊዜ አዘጋጅተናል። ከቅርንጫፍ ቢያንስ አንድ ሰው እንዲሳተፍ ግዴታ ነው።*

*የእያንዳንዱ ቅርንጫፍ ዲጂታል አምባሳደሮች መሳተፍ አለባቸው።*

*🕧 ሰአት: ቅዳሜ ጠዋት 3:00*

🔥 Title:  A Request for Second Round Online Session

Anbesa Plus Rollout Second Round Online Session
Saturday, February 14, 2026
9:00 AM  |  (UTC+03:00) Nairobi  |  2 hrs 30 mins

Meeting number (access code):  * 2554 485 2539*
Meeting password:   *MB@ab1*
*
When it's time, click the link below.
https://anbesabank.webex.com/anbesabank/j.php?MTID=mb87517a0b86da76cd320a073a946fce9  *
"""
        await update.message.reply_text(
            response,   
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
    
    # How to login to DBS backoffice
    elif user_message == "How to login to DBS backoffice":
        response = """Steps to Log in to DBS Backoffice
Video Tutorial: https://t.me/anbesaplus/2252
"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return

    # Digital Access Approval on CBS (Manual Review)
    elif user_message == "Digital Access Approval on CBS (Manual Review)":
        caption = """Steps for Digital Access Approval on CBS (Manual Review)
"""
#  caption = """Steps to approve of Digital Access on CBS (Manual Review)
# Video Tutorial: https://t.me/anbesaplus/12636
# """
        await send_cached_file(update, "Approve_of_Digital_Access_on_CBS_video", caption=caption,parse_mode="Markdown")

        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return

    # Overlay Detected Avoid Entering Sensetive Information Error
    elif user_message == "Overlay Detected Avoid Entering Sensetive Information Error":
        response = """This error occurs when your device detected an app on top of Anbesa Plus—for example, a screen recorder or any app that can display over other apps. This is a security measure to protect sensitive information like passwords, PINs, or payment details.

*ይህ የሚያጋጥመው ስልክዎ በአንበሳ ፕላስ መተግበሪያ ላይ ተጨማሪ ሌላ መተግበሪያ ሲያገኝ ሲሆን ለምሳሌ Screen Recorder ወይም ሌሎች መተግበሪያዎች ሊሆኑ ይችላሉ።ይህም የይለፍ ቃላት(Password)፣ ፒን(Pin) ወይም ሌሎች የክፍያ ዝርዝሮች እና ሚስጥራዊነት ያላቸውን መረጃዎች ለመጠበቅ የተደረገ የደህንነት እርምጃ ነው።*


 Steps to Fix This Overlay Warning

1️⃣ ⚙️ Open Settings on your phone.

2️⃣ 📱 Go to Apps.

3️⃣  ⋮  Tap the three dots at the top-right → select Special app access.

4️⃣  Choose Display over other apps (sometimes called Draw over other apps or Appear on top).

Look for apps that may create overlays:
Example: Screen recorders, Floating widgets or notepads, Screen dimming apps

5️⃣ Temporarily disable these apps.

🔙 Go back to Anbesa Plus and try again

💡 Tip: After finishing your sensitive actions, you can re-enable any apps you need.
"""
        
        await update.message.reply_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
    
    # What branches do when the customer is blocked
    elif user_message == "What branches do when the customer is blocked":
        caption = """
https://t.me/anbesaplus/12418

Branches need to know the difference between Blocked and Locked:
ቅርንጫፎች *በታገዷል* እና *በተቆልፏል* መካከል ያለውን ልዩነት ማወቅ አለባቸው።

- *⛔ Blocked*: Only Head Office (Third-Level Support) can fix this. When they unblock it, it applies to everyone at once—not just one customer.
*Blocked ማለት ታግዷል ሲሆን በዋናው መ/ቤት የሶስተኛ ደረጃ ድጋፍ ብቻ ነው መስተካከል የሚችለው። እገዳውን ሲያነሱት ለሁሉም በአንድ ጊዜ እንጂ ደንበኛ በደንበኛ አይደለም ስለዚህ ጥያቄያችሁን ልካችሁ እስኪስተካከል በትዕግስት ጠብቁ።*

- *🔓 Locked*: The branch can fix this themselves by unlocking it directly in the DBS back office system.
*Locked ​ማለት ተቆልፏል ሲሆን ቅርንጫፍ ላይ በቀጥታ DBS back office system በመጠቀም ማስተካከል ይቻላል።*

⚠️ Before sclaating the problem to the Head Office, branches should check if the customer is Blocked or Locked. If it's Blocked also make sure the status in the BackOffice system is also Blocked then try to reset it.

ችግሩን ወደ ዋናው መሥሪያ ቤት ከመላኩ በፊት ቅርንጫፍ ላይ በደንበኛው ስልክ የታገደ መሆኑን ማረጋገጥ አለባቸው። ከታገደ በBackOffice ሁኔታ መታገዱን ያረጋግጡ ከዚያም እንደገና ለማስጀመር ይሞክሩ።
"""
        await send_cached_file(update, "blocked_customer_video", caption=caption,parse_mode="Markdown")

    # How Anbesa Plus supports local language
    elif user_message == "How Anbesa Plus supports local language":
        response = """Anbesa Plus supports local language options in the app:
Video Tutorial: https://t.me/anbesaplus/1676
"""
    
        await update.message.reply_text(
            response,  parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
    
    # How to release trusted device
    elif user_message == "How to release trusted device":
        response = """How to release trusted device
Video Tutorial: https://t.me/anbesaplus/2133
                """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    
    # How to search customer in DBS backoffice
    elif user_message == "How to search customer in DBS backoffice":
        response = """How to search customer in DBS backoffice
Video tutorial: https://t.me/anbesaplus/2131"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    
    # How Forgot password works
    elif user_message == "How Forgot password works":
        response = """How Forgot password works
Video Tutorial: https://t.me/anbesaplus/1611."""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return

    # Download Anbesa Plus Application
    elif user_message == "⬇️ Download Anbesa Plus Application":
        await update.message.reply_text(
            "Select your device type:",
        reply_markup=get_app_download_menu()
    )
        return

    # Android App Download link 
    elif user_message == "Android App Download Link":
        response = """🔗 Download the AnbesaPlus Android App from:
        https://downloads.anbesabank.com/ """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
            # reply_markup=get_app_download_menu()

        )
        return
    # Iphone App Download Link 
    elif user_message == "Iphone App Download Link":
        response = """
❗️❗️ *These steps are temporary until the production app is officially released on the App Store.* ❗️❗️

Steps to Download TestFlight and Install Anbesa Plus.

1. Open the App Store on your Iphone.

2. Search for *TestFlight* in the search bar.

3. Download and install TestFlight.
	Authenticate if needed (Face ID, Touch ID, or Apple ID password).

4. Once TestFlight is installed.

5. Open the link below to download Anbesa Plus.

6. Tap *Install* in TestFlight to download Anbesa Plus.

7. Open Anbesa Plus from TestFlight and start using it.

🔗 Download the AnbesaPlus Iphone App from:
        https://testflight.apple.com/join/Mz5erFuA """
        
        await update.message.reply_text(
            response,   parse_mode="Markdown",
            reply_markup=get_main_keyboard()
            # reply_markup=get_app_download_menu()

        )
        return
    # # Reported And Fixed Issues Menu
    # elif user_message == "Reported And Fixed Issues":
    #     await update.message.reply_text(
    #         "Reported And Fixed Issues Menu",
    #     reply_markup=get_reported_and_fixed_issues_menu()
    # )
    #     return

    # # Fixed Phone Number Already Exists Issues 
    # elif user_message == "Fixed Phone Number Already Exists Issues":
    #     response = """Fixed Phone Number Already Exists Issues
    #     """
    #     await update.message.reply_text(
    #         response,
    #         reply_markup=get_reported_and_fixed_issues_menu()
    #     )
    #     return
    # # Fixed Blocked User/Account Issues
    # elif user_message == "Fixed Blocked User/Account Issues":
    #     response = """Fixed Blocked User/Account Issues
    #     """
    #     await update.message.reply_text(
    #         response,
    #         reply_markup=get_reported_and_fixed_issues_menu()
    #     )
    #     return
    # # Fixed Automatically Returning to Login Screen Issues
    # elif user_message == "Fixed Automatically Returning to Login Screen Issues":
    #     response = """Fixed Automatically Returning to Login Screen Issues
    #     """
    #     await update.message.reply_text(
    #         response,
    #         reply_markup=get_reported_and_fixed_issues_menu()
    #     )
    #     return
    
        # DBS End User Manual for Branches
    elif user_message == "DBS End User Manual for Branches":
        response = """Get the DBS End User Manual for Branches:
    https://t.me/anbesaplus/1199 """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    
        # DBS Back Office / Portal User Access Request Form
    elif user_message == "DBS Back Office / Portal User Access Request Form":
        response = """Get DBS Back Office / Portal User Access Request Form:
    https://t.me/anbesaplus/3646 """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    # Backoffice User Access Updates
    elif user_message == "Backoffice User Access Updates":
        response = """📢 Backoffice User Access Updates
Upto this week (17/February) the remaining branches who are not granted access DBS backoffice are the following:

 1. Adi Kelebes
 2. Adishihu
 3. Adi_daero
 4. Adwa
 5. Aynalem
 6. Agazian
 7. Assosa
 8. Awlaelo
 9. Beshale
10. Boditi
11. CMC
12. Debre Tabor
13. Dera
14. Edagahamus
15. Edagakedam
16. Edagarebue
17. Furi
18. Ginbgebeya
19. Ifb Kukufto
20. Kality
21. Kandearo
22. Karakore
23. Megenagn Athletderartu
24. Seket
25. Selekleka
26. Semema
27. Shollagebeya
28. Tuludimtu
29. Weyni

SMS has already been sent. Those who haven’t requested access yet must request it. If you requested this week, wait for notifications — we’ll send them soon. 
You are adviced to follow instructions. Use the request form we have shared to you. You can find it in this group or in the bot menu.
https://t.me/anbesaplus/3646
"""
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    # Announcements for Invalid Backoffice Requests
    elif user_message == "❗️Announcements for Invalid Backoffice Requests":
        response = """Upto this week (17/February)
Branches who submitted requests earlier but did not receive access:
ቀደም ሲል ጥያቄ አቅርባችሁ እስካሁን ፈቃድ (Access) ላልተሰጣችሁ ቅርንጫፎች፣ መዘግየቱ አብዛኛውን ጊዜ የሚፈጠረው ስህተት ከሆነ አሞላል የተያያዘ ነው። በመሆኑም በድጋሚ ጥያቄ ከማቅረባችሁ በፊት የሚከተሉትን ነጥቦች አረጋግጡ::

```
1.  Adi Mehameday          23. Kalamin
2.  Adiabum                24. Kality
3.  Adihaki Market         25. Keta
4.  Adisalem               26. Mariam Quiha
5.  Adwa                   27. Maymekden
6.  Agaro                  28. Meda agame
7.  Ahferom                29. MekanisaABO
8.  Aradagiorgis           30. MEZBIR
9.  Ardijeganu             31. Parlama
10. Atote                  32. Sarbet
11. Atsbi                  33. Sebeya
12. Aweday                 34. Seket
13. Ayat Tafo              35. Semera
14. Berahle                36. Shire Edaga
15. Bethel                 37. Suhul shire
16. Boditi                 38. Tana
17. BoleArabsa             39. Warabe
18. Endabaguna             40. Welwalo
19. Erdiseganu             41. Wollosefer
20. GojamBerenda           42. Wuhalimat
21. Guroro                 43. Yechila
22. Injibara

```
Common reasons for delay or rejection:

 1️⃣ Some requests may not be processed if not forwarded by IT Support to digital technology, If you believe your request is delayed and you have not received any response in Help Desk. 
    please send, Branch name and ticket number to the following users: @tokeyj or @Fish\_dt
 
 2️⃣ Requests submitted without full name or complete user information.

 3️⃣ Submitting fewer than the required users or more than the allowed maximum
 
 4️⃣ Requests submitted without clear and readable round stamp
 
 5️⃣ Requests submitted for Branch Managers (these roles are not assigned Back Office access)
 
 6️⃣ Not using the official Anbesa Plus DBS Back Office Request Form

 7️⃣ Missing Branch Manager approval where required

*❗️ Reminder – Allowed Users per Branch:*

- Each branch may submit **only 2 users**: 1 CSO and 1 Accountant/ CSM
- Additionally, a branch may submit **1 Auditor**, only if the branch has an assigned auditor

"""
        await update.message.reply_text(
            response,  parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
        
# When OTP is not reaching to the customer's mobile
    elif user_message == "When OTP is not reaching to the customer's mobile":
        response = """
📱 When OTP is not reaching the customer's mobile

1️⃣ Verify SMS reception

Confirm if the customer receives SMS from any sender.

2️⃣ Check sender-specific blocking

If other SMS are received, verify whether messages from Anbesabank / LIB / 8803 are blocked on the customer’s device.

If blocked, unblock immediately.

3️⃣ Ensure phone accessibility

If not blocked, confirm the customer’s phone is reachable for both calls and SMS (network coverage, SIM active, not in airplane mode).

4️⃣ Validate head office SMS service

If all above checks pass, confirm whether SMS service is temporarily stopped at the Head Office.

⚠️ Note: This occurs in <2% of cases, so check steps 1–3 first.
"""
        await context.bot.send_message(
    chat_id=update.effective_chat.id, 
    text=response,
    reply_markup=get_main_keyboard()
)
        return

# ALREADY EXISTING PHONE NO
    elif user_message == "ALREADY EXISTING PHONE NO":
        response = """
When a customer’s status shows *“ALREADY EXISTING PHONE NO”*, it means they tried to set up Digital Access but didn’t finish, for different reasons. First Branches must check if the phone number is in the DBS backoffice. If it doesn’t exist in the DBS backoffice , follow these steps

- 	If the customer forgot their password, they cannot fix it themselves. They must wait for us to reset it so they can start fresh.

- 	To reset, Third-Level Support (IT–Digital Banking) checks whether the customer has already clicked “Forgot Password” and been disabled.

- 	So, the customer must first initiate *“Forgot Password.”*

- 	After that, they need to wait until IT–Digital Banking completes the reset. This is done for all affected customers at once, not individually.

⚠️ Note: IT–Digital Banking usually performs this reset at least twice a week.

"""
        await context.bot.send_message(
    chat_id=update.effective_chat.id, 
    text=response,parse_mode="Markdown",
    reply_markup=get_main_keyboard()
)
        return

    elif user_message == "Designation of Digital Ambassador at Branches":
        caption='''Dear colleagues,
In accordance with the attached internal memo, please designate one representative for each branch. Kindly note that GRO has already completed this exercise at the district level and provided us with district-by-district lists.

While we have received responses from some branches, we now require a consolidated list covering all branches.

Your prompt cooperation in providing this information will be greatly appreciated.
'''
        await send_cached_file(update, "digital_ambassador_pdf", caption=caption,parse_mode="Markdown")
        return

    elif user_message == "Report Issues":
        response = """To report any issues or problems use the following Telegram Bot @AnbesaPlusIssueReportingBot"""
        await update.message.reply_text(
            response,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
     # Back to main
    elif user_message == "🔙 Back" or user_message == "🏠 Main Menu":
        await update.message.reply_text(
            "Return to Main menu",
            reply_markup=get_main_keyboard()
    )
        return
    
    # Help command from keyboard
    elif user_message == "/help" or user_message.lower() == "help":
        await help_command(update, context)
        return
    


async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome when bot is added to a group"""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:  # If the new member is our bot
            welcome_text = """AnbesaPlus Helper Bot has joined!
To start: Type /start or select from menu below"""
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=get_main_keyboard()
            )
            logger.info(f"Bot added to group: {update.effective_chat.title}")
            
        return

# ===== ERROR HANDLER =====
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ===== MAIN FUNCTION =====
def main():
    """Start the bot"""
    print("=" * 50)
    print("STARTING AnbesaPLUS HELPER BOT")
    print("=" * 50)
    
    # 1. Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 2. Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # 3. Handle when bot is added to group
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, 
        new_chat_members
    ))
    
    
    # 4. Handle all text messages (button clicks)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_message
    ))
    
    # 5. Add error handler
    application.add_error_handler(error_handler)
    
    # 6. Start polling
    print("Bot is running...")
    print("Add me to your Telegram group!")
    print("=" * 50)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# ===== START THE BOT =====
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")