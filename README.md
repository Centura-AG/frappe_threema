# Frappe Threema

**Frappe Threema** is a Threema integration for the Frappe framework, using the official [Threema API](https://gateway.threema.ch/en/developer/api). Currently, the integration supports only  **Basic mode**.

## Features
- Seamlessly integrates Threema messaging within Frappe.
- Allows sending messages through "Threema Center" or using "Notification".
- Adds a "Threema ID" field to the User Doctype, prioritizing it as the contact method when using the Threema integration. If unavailable, it fallback to mobile number or email.

## Installation

### Step 1: Install the App
```bash
bench get-app https://github.com/Centura-AG/app_frappe_threema
```
### Step 2: Install the App on a specific Site
```bash
bench --site [sitename] install-app app_frappe_threema   `
```
### Step 3: Configure Threema Settings

*   Go to **Threema Settings** in your Frappe instance.
*   Enter your Threema API credentials.
    

Usage
-----

*   **Send Messages**: You can send messages directly via the **Threema Center** or set up **Notifications** to automate messaging.
*   **Threema Message Log** Will log what all messages sent via the Threema integration.
    

License
-------

This project is licensed under the [MIT License](LICENSE).
