import json
import smtplib
import time
import os
from jinja2 import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Personal information from .env
MY_NAME = os.getenv("MY_NAME")
MY_EMAIL = os.getenv("MY_EMAIL")
MY_PHONE = os.getenv("MY_PHONE")
MY_RESUME_PATH = os.getenv("MY_RESUME_PATH")

# Email configuration from .env
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("EMAIL_USERNAME")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")
TEST_EMAIL = os.getenv("TEST_EMAIL")

# API keys from .env
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Load company details from JSON
with open("companies.json", "r", encoding="utf-8") as file:
    companies = json.load(file)

# Email templates using Jinja2
email_template_en = f"""
Dear {{{{ contact_person }}}},

I hope this email finds you well. My name is {MY_NAME}, and I am currently seeking an internship opportunity in Web Development. I am very interested in joining {{{{ name }}}} and believe my skills align with your company's vision.
    
I have attached my CV for your review. I would appreciate the opportunity to discuss further.

Looking forward to your response.

Best regards,  
{MY_NAME}
phone: {MY_PHONE},
email: {MY_EMAIL}
"""

email_template_fr = f"""
Cher {{{{ contact_person }}}},

J'espère que cet email vous trouve bien. Je m'appelle {MY_NAME} et je suis actuellement à la recherche d'un stage en développement Web. Je suis très intéressé par rejoindre {{{{ name }}}} et je crois que mes compétences sont en adéquation avec la vision de votre entreprise.
    
Vous trouverez ci-joint mon CV pour votre examen. Je serais ravi de pouvoir en discuter davantage.

Dans l'attente de votre réponse.

Cordialement,  
{MY_NAME}
téléphone: {MY_PHONE},
email: {MY_EMAIL}
"""

def send_email(to_email, subject, body, attachment_path):
    """Sends an email with an attachment using SMTP."""
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach the PDF file
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {attachment_path}",
            )
            msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email}")

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

def get_company_info_from_gemini(api_key, company_name, city=None):
    """Fetch company details using Google Gemini AI."""
    client = genai.Client(api_key=api_key)
    
    try:
        # Build a more specific prompt using company name and city
        location_info = f" in {city}" if city else ""
        prompt = f"""
        Provide factual information about {company_name}{location_info} company. 
        Include details about:
        - Their main business activities
        - Size of the company (if available)
        - Notable achievements or projects
        - Technology stack they use (if it's a tech company)
        
        Focus only on providing factual information. Do not recommend any actions, 
        investments, or personal opinions. Do not suggest contacting the company 
        or visiting their locations.
        
        Format your response in Markdown with appropriate headings, bullet points, 
        and sections for easy readability. Use ## for main sections and * for bullet points.
        """
        
        # Query Gemini AI for information about the company
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"❌ Failed to get information from Gemini AI: {e}")
        return None

def save_company_info_to_file(company_info_dict):
    """Save company information to a text file with nice formatting."""
    filename = "company_information.md"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write("=" * 80 + "\n")
            file.write("COMPANY INFORMATION REPORT\n")
            file.write("=" * 80 + "\n\n")
            
            for company_name, info in company_info_dict.items():
                file.write("-" * 80 + "\n")
                file.write(f"COMPANY: {company_name}\n")
                file.write("-" * 80 + "\n\n")
                file.write(f"{info}\n\n")
            
        print(f"✅ Company information saved to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Failed to save company information to file: {e}")
        return False

def generate_ai_email(api_key, company_name, contact_person, city=None, language="English"):
    """Generate personalized email content and subject using Google Gemini AI based on company details."""
    client = genai.Client(api_key=api_key)
    
    try:
        location_info = f" in {city}" if city else ""
        
        if language == "French":
            # Generate email body
            body_prompt = f"""
            Écris un email professionnel en français pour une candidature de stage en développement Web à {company_name}{location_info}.
            L'email doit:
            - Être adressé à {contact_person}
            - Mentionner mon intérêt spécifique pour {company_name} et pourquoi je voudrais y travailler
            - Mentionner que mon CV est joint
            - Être concis (maximum 5-6 phrases)
            - Avoir un ton formel mais chaleureux
            - Se terminer par "Dans l'attente de votre réponse. Cordialement, {MY_NAME}"
            - Ne pas inclure d'informations inventées sur l'entreprise
            - S'assurer que je suis clairement identifié comme {MY_NAME} (pas de placeholder comme [Votre Nom])
            
            IMPORTANT: 
            - N'inclus pas d'objet d'email ou de pièce jointe dans ton texte
            - N'inclus pas de commentaires, notes, ou explications
            - N'utilise pas de balises de formatage (markdown, html, etc.)
            - Le texte doit être prêt à l'envoi exactement comme tu le fournis
            - Ne commence pas par "Voici un email..." ou des phrases similaires
            """
            
            # Generate email subject
            subject_prompt = f"""
            Crée un objet d'email concis et professionnel en français pour une candidature de stage en développement Web à {company_name}.
            L'objet doit:
            - Être court (maximum 60 caractères)
            - Être direct et clair
            - Mentionner qu'il s'agit d'une candidature de stage de {MY_NAME}
            - Ne pas contenir de point à la fin
            - Ne pas contenir de placeholders comme [Votre Nom]
            - Ne pas contenir de guillemets, de préfixes ou d'autres symboles non nécessaires
            
            IMPORTANT:
            - Réponds uniquement avec l'objet de l'email, rien d'autre
            - Ne commence pas par "Objet:" ou "Sujet:"
            - N'utilise pas de formatage spécial
            """
        else:
            # Generate email body
            body_prompt = f"""
            Write a professional email in English for an internship application in Web Development to {company_name}{location_info}.
            The email should:
            - Be addressed to {contact_person}
            - Mention my specific interest in {company_name} and why I would like to work there
            - Mention that my CV is attached
            - Be concise (maximum 5-6 sentences)
            - Have a formal but warm tone
            - End with "Looking forward to your response. Best regards, {MY_NAME}"
            - Not include made-up information about the company
            - Make sure I'm clearly identified as {MY_NAME} (no placeholders like [Your Name])
            
            IMPORTANT:
            - Do not include email subject or attachment notes in your text
            - Do not include any comments, notes, or explanations
            - Do not use any formatting tags (markdown, html, etc.)
            - The text should be ready to send exactly as you provide it
            - Do not start with "Here's an email..." or similar phrases
            """
            
            # Generate email subject
            subject_prompt = f"""
            Create a concise and professional email subject line in English for a Web Development internship application to {company_name}.
            The subject should:
            - Be short (maximum 60 characters)
            - Be direct and clear
            - Mention it's an internship application from {MY_NAME}
            - Not end with a period
            - Not contain placeholders like [Your Name]
            - Not contain quotes, prefixes or other unnecessary symbols
            
            IMPORTANT:
            - Only respond with the email subject line, nothing else
            - Do not start with "Subject:" or similar prefixes
            - Do not use any special formatting
            """
        
        # Generate email body
        body_response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=body_prompt
        )
        
        # Generate email subject
        subject_response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=subject_prompt
        )
        
        # Clean up the responses
        email_body = body_response.text.strip() if body_response.text else None
        email_subject = subject_response.text.strip() if subject_response.text else None
        
        # Post-processing to remove any remaining artifacts
        if email_body:
            # Remove any markdown or formatting markers
            email_body = email_body.replace('```', '').replace('markdown', '')
            # Remove any lines that might be AI comments
            lines = email_body.split('\n')
            clean_lines = []
            for line in lines:
                if not line.startswith(('Here is', 'Voici', 'Note:', 'Here\'s', 'I hope', 'This email')):
                    clean_lines.append(line)
            email_body = '\n'.join(clean_lines).strip()
        
        if email_subject:
            # Remove any quotes, "Subject:", etc.
            email_subject = email_subject.replace('"', '').replace("'", '').strip()
            if email_subject.lower().startswith('subject:'):
                email_subject = email_subject[8:].strip()
            if email_subject.lower().startswith('objet:'):
                email_subject = email_subject[6:].strip()
        
        return email_subject, email_body
        
    except Exception as e:
        print(f"❌ Failed to generate personalized email: {e}")
        return None, None

def display_generated_email(company_name, contact_person, email_subject, email_body, language):
    """Display a generated email in the console with nice formatting."""
    print("\n" + "=" * 80)
    print(f"📧 PREVIEW: AI-GENERATED EMAIL FOR {company_name} ({language})")
    print("=" * 80)
    print(f"SUBJECT: {email_subject}")
    print("-" * 80)
    print("\n" + email_body + "\n")
    print("-" * 80 + "\n")

def update_companies_sent_status(companies_sent):
    """Update the is_sent status in the companies.json file."""
    try:
        # Read the current JSON file
        with open("companies.json", "r", encoding="utf-8") as file:
            companies = json.load(file)
        
        # Update the is_sent status for companies that were sent emails
        for company in companies:
            if company["name"] in companies_sent:
                company["is_sent"] = True
        
        # Write the updated data back to the file
        with open("companies.json", "w", encoding="utf-8") as file:
            json.dump(companies, file, indent=4)
        
        print("✅ Companies JSON file updated successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to update companies JSON file: {e}")
        return False

# Menu for user to choose action
print("Please choose an option:")
print("1. Send emails to companies")
print("2. Fetch company information using Google Gemini AI")
print("3. Test AI email generation (no emails sent)")
option = input("Enter your choice (1, 2 or 3): ")

if option == "1":
    # Ask if the user wants to use AI-generated emails or templates
    email_option = input("How would you like to generate emails?\n1. Use AI to personalize each email\n2. Use standard templates\nEnter your choice (1 or 2): ")
    use_ai = email_option == "1"
    
    # Ask if the user wants to send in test mode or actual mode
    test_option = input("Do you want to test emails or send actual emails?\n1. Test mode (send to test inbox)\n2. Actual mode (send to companies)\nEnter your choice (1 or 2): ")
    
    template_en = Template(email_template_en)
    template_fr = Template(email_template_fr)
    attachment_path = MY_RESUME_PATH  # Update with the actual path to your PDF
    
    # Test mode will send all emails to the test inbox
    test_mode = test_option == "1"
    test_email = TEST_EMAIL
    
    # Keep track of sent companies and skipped companies
    companies_sent = []
    companies_skipped = []
    
    for company in companies:
        company_name = company["name"]
        
        # Skip companies that have already been sent emails (only in actual mode)
        if not test_mode and company.get("is_sent", False):
            print(f"⏭️ Skipping {company_name} - Email already sent previously")
            companies_skipped.append(company_name)
            continue
            
        contact_person = company["contact_person"]
        city = company.get("city", None)
        language = company.get("language", "English")
        
        if use_ai:
            print(f"Generating AI personalized email for {company_name}...")
            email_subject, email_body = generate_ai_email(
                gemini_api_key, 
                company_name, 
                contact_person, 
                city, 
                language
            )
            
            # Fall back to templates if AI generation fails
            if not email_body:
                print(f"⚠️ AI email generation failed for {company_name}, using template instead.")
                if language == "French":
                    email_body = template_fr.render(name=company_name, contact_person=contact_person)
                else:
                    email_body = template_en.render(name=company_name, contact_person=contact_person)
                # Default subject if AI subject generation failed
                email_subject = f"Internship Application - {company_name}"
        else:
            # Use template emails
            if language == "French":
                email_body = template_fr.render(name=company_name, contact_person=contact_person)
            else:
                email_body = template_en.render(name=company_name, contact_person=contact_person)
            # Default subject for template emails
            email_subject = f"Internship Application - {company_name}"

        # If in test mode, send to test email, otherwise send to actual company email
        recipient_email = test_email if test_mode else company["email"]
        
        # Create a log subject with prefix (for display only)
        log_subject = f"[{'AI' if use_ai else 'Template'} {'TEST' if test_mode else 'ACTUAL'}] {email_subject}"
        
        # Send email with the clean subject (no prefix)
        send_email(recipient_email, email_subject, email_body, MY_RESUME_PATH)
        
        # Log with the prefixed subject
        print(f"Email with subject '{log_subject}' sent to {recipient_email}")
        
        # Add to sent list if in actual mode
        if not test_mode:
            companies_sent.append(company_name)
            
        time.sleep(5)  # Delay to avoid spam detection

    # Display summary
    if test_mode:
        print(f"✅ All test emails sent to {test_email}!")
        print("ℹ️ Note: No companies were marked as 'sent' since this was a test.")
    else:
        # Update the companies.json file with sent status
        if companies_sent:
            update_companies_sent_status(companies_sent)
            print(f"✅ Sent emails to {len(companies_sent)} companies!")
        
        if companies_skipped:
            print(f"ℹ️ Skipped {len(companies_skipped)} companies that were already sent emails.")

elif option == "2":
    company_info_dict = {}
    for company in companies:
        city = company.get("city", None)  # Get the city if available
        print(f"Fetching information for {company['name']}...")
        info = get_company_info_from_gemini(gemini_api_key, company["name"], city)
        if info:
            print(f"Information retrieved for {company['name']}")
            company_info_dict[company["name"]] = info
        time.sleep(3)  # Delay between API calls
    
    # Ask user if they want to save the information to a file
    if company_info_dict:
        save_option = input("Do you want to save the company information to a file? (y/n): ")
        if save_option.lower() == 'y':
            save_company_info_to_file(company_info_dict)
    else:
        print("No company information was retrieved.")

elif option == "3":
    print("\n📝 Testing AI email generation - previewing emails without sending them...")
    
    # Store generated emails to potentially send them later
    generated_emails = {}
    
    # Loop through each company
    for company in companies:
        company_name = company["name"]
        contact_person = company["contact_person"]
        city = company.get("city", None)
        language = company.get("language", "English")
        
        print(f"Generating AI personalized email for {company_name}...")
        email_subject, email_body = generate_ai_email(
            gemini_api_key, 
            company_name, 
            contact_person, 
            city, 
            language
        )
        
        # Store the generated email
        if email_body:
            generated_emails[company_name] = {
                "subject": email_subject or f"Internship Application - {company_name}",
                "body": email_body,
                "language": language,
                "contact_person": contact_person
            }
            # Display the generated email
            display_generated_email(company_name, contact_person, email_subject, email_body, language)
        else:
            print(f"⚠️ AI email generation failed for {company_name}")
            
        time.sleep(2)  # Small delay between API calls
    
    print("\n✅ All test emails generated and displayed.")
    
    # Ask if user wants to take action with the emails
    if generated_emails:
        send_option = input("\nWhat would you like to do with these emails?\n"
                           f"1. Send all test emails to my inbox ({TEST_EMAIL})\n"
                           "2. Proceed with normal sending options\n"
                           "3. Exit without sending\n"
                           "Enter your choice (1, 2, or 3): ")
        
        if send_option == "1":
            # Send all emails directly to test inbox
            test_email = TEST_EMAIL
            attachment_path = MY_RESUME_PATH
            
            print(f"\nSending all test emails to {test_email}...")
            
            for company_name, email_data in generated_emails.items():
                email_body = email_data["body"]
                email_subject = email_data["subject"]
                
                # For logging purposes only
                print(f"Sending email about {company_name}...")
                
                # Send with clean subject (no prefix)
                send_email(test_email, email_subject, email_body, attachment_path)
                time.sleep(3)  # Shorter delay for test emails
                
            print(f"✅ All test emails sent to {test_email}!")
            print("ℹ️ Note: No companies were marked as 'sent' since this was a test.")
            
        elif send_option == "2":
            # Continue with the normal sending process
            # Ask if test mode or actual mode
            test_option = input("1. Test mode (send to test inbox)\n2. Actual mode (send to companies)\nEnter your choice (1 or 2): ")
            
            template_en = Template(email_template_en)
            template_fr = Template(email_template_fr)
            attachment_path = MY_RESUME_PATH
            
            # Test mode will send all emails to the test inbox
            test_mode = test_option == "1"
            test_email = TEST_EMAIL
            
            # Keep track of sent companies and skipped companies
            companies_sent = []
            companies_skipped = []
            
            for company in companies:
                company_name = company["name"]
                
                # Skip companies that have already been sent emails (only in actual mode)
                if not test_mode and company.get("is_sent", False):
                    print(f"⏭️ Skipping {company_name} - Email already sent previously")
                    companies_skipped.append(company_name)
                    continue
                
                # Use the already generated email if available
                if company_name in generated_emails:
                    email_body = generated_emails[company_name]["body"]
                    email_subject = generated_emails[company_name]["subject"]
                else:
                    # This should not happen, but just in case
                    contact_person = company["contact_person"]
                    city = company.get("city", None)
                    language = company.get("language", "English")
                    
                    print(f"Re-generating email for {company_name}...")
                    email_subject, email_body = generate_ai_email(
                        gemini_api_key, 
                        company_name, 
                        contact_person, 
                        city, 
                        language
                    )
                    
                    # Fall back to templates if AI generation fails
                    if not email_body:
                        print(f"⚠️ AI email generation failed for {company_name}, using template instead.")
                        if language == "French":
                            email_body = template_fr.render(name=company_name, contact_person=contact_person)
                        else:
                            email_body = template_en.render(name=company_name, contact_person=contact_person)
                        email_subject = f"Internship Application - {company_name}"
                
                # If in test mode, send to test email, otherwise send to actual company email
                recipient_email = test_email if test_mode else company["email"]
                
                # For logging purposes only
                if test_mode:
                    print(f"Sending test email about {company_name}...")
                else:
                    print(f"Sending actual email to {company_name}...")
                
                # Send with clean subject (no prefix)
                send_email(recipient_email, email_subject, email_body, attachment_path)
                
                # Add to sent list if in actual mode
                if not test_mode:
                    companies_sent.append(company_name)
                    
                time.sleep(5)  # Delay to avoid spam detection
            
            # Display summary
            if test_mode:
                print(f"✅ All test emails sent to {test_email}!")
                print("ℹ️ Note: No companies were marked as 'sent' since this was a test.")
            else:
                # Update the companies.json file with sent status
                if companies_sent:
                    update_companies_sent_status(companies_sent)
                    print(f"✅ Sent emails to {len(companies_sent)} companies!")
                
                if companies_skipped:
                    print(f"ℹ️ Skipped {len(companies_skipped)} companies that were already sent emails.")
                
        else:
            print("📪 No emails sent. Exiting...")
    else:
        print("No valid emails were generated. Exiting...")

else:
    print("❌ Invalid option. Please choose 1, 2, or 3.")
