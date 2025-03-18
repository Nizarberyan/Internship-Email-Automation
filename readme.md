# Internship Application Automation

This project automates the process of sending internship application emails to various companies. It uses Python for scripting, Jinja2 for templating emails, and Google Gemini AI for generating personalized email content.

## Project Structure

- `companies.json`: Contains the list of companies to which the applications will be sent.
- `internship.py`: The main script that handles email sending and AI-based email generation.

## JSON Structure

The `companies.json` file should have the following structure:

```json
[
  {
    "name": "string",
    "email": "string",
    "contact_person": "string",
    "position": "string",
    "language": "string",
    "city": "string",
    "phone": "string (optional)",
    "is_sent": "boolean"
  }
]
```

## Setup Instructions

1. Clone the repository:

   ```sh
   git clone https://github.com/Nizarberyan/Internship-Email-Automation.git
   cd internship-automation
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your environment variables:
   ```env
   MY_NAME=Your Name
   MY_EMAIL=your.email@example.com
   MY_PHONE=+1234567890
   MY_RESUME_PATH=/path/to/your/resume.pdf
   SMTP_SERVER=smtp.example.com
   SMTP_PORT=587
   EMAIL_USERNAME=your.email@example.com
   EMAIL_PASSWORD=yourpassword
   TEST_EMAIL=test.email@example.com
   GEMINI_API_KEY=your_gemini_api_key
   ```

## Usage

1. Ensure your `companies.json` file is correctly populated with the company details.
2. Run the `internship.py` script to start sending emails:
   ```sh
   python internship.py
   ```

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.
