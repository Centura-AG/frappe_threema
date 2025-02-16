# Frappe Threema

## Overview
Frappe Threema is a seamless integration between the Frappe framework and Threema messaging service, leveraging the official [Threema Gateway API](https://gateway.threema.ch/en/developer/api). This integration currently operates in **Basic mode**, providing a robust solution for secure messaging within your Frappe applications.

## Features
- Direct integration with Threema Gateway API
- Message sending through Threema Center
- Automated messaging via Notification system
- Comprehensive message logging
- Secure end-to-end communication
- Easy-to-use interface within Frappe

## Requirements
- Frappe v15+

## Installation
You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app frappe_threema
```

## Configuration

1. Navigate to **Threema Settings** in your Frappe instance
2. Configure the following:
   - Threema API Key
   - Gateway ID
   - Password
3. Save your settings

## Usage

### Threema Center
- Access the Threema Center to send direct messages
- Compose and send messages to Threema users
- View message status and delivery reports

### Notifications
- Set up automated messages
- Configure notification triggers
- Customize message templates

### Message Logging
- Track all sent messages in Threema Message Log
- Monitor delivery status
- Access message history

## Support
For support and issues, please create a new issue.

## License
MIT License - See LICENSE file for details
