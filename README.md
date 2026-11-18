# Frappe Threema

Send [Threema](https://threema.ch) messages from Frappe, by hand or automatically through Notifications.

Frappe Threema uses the [Threema Gateway](https://gateway.threema.ch) in **Basic mode** (`send_simple`). In Basic mode, Threema encrypts each message on its server before delivery, so you need no key management on your side.

## Features

- **Threema Center**: send a message by hand to one or more receivers.
- **Notifications**: a new channel "Threema" for Frappe Notifications, with receivers taken from phone and mobile fields of the document, from its owner or from a role.
- **Threema Message Log**: every message the gateway accepted, with sender, receivers and time.
- Receivers can be a Threema ID, a mobile number or an email address that is linked to a Threema account.

## Requirements

- Frappe v16, branch `develop`
- Frappe v15, branch `version-15`
- A Threema Gateway ID for Basic mode and its API secret

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Centura-AG/frappe_threema --branch develop
bench --site $SITE install-app frappe_threema
```

## Configuration

Open **Threema Settings** and fill in:

| Field       | Value                                                        |
| ----------- | ------------------------------------------------------------ |
| Gateway URL | `https://msgapi.threema.ch/send_simple`                      |
| Gateway ID  | Your Gateway ID, starting with `*`, e.g. `*ABC1234`          |
| Secret      | The API secret of the Gateway ID, from the Gateway dashboard |

## Usage

### Threema Center

Enter one receiver per line and a message, then click **Send Message**. A receiver is one of:

- a Threema ID with 8 characters, e.g. `ABCD1234`
- a mobile number in international format, e.g. `41791234567`
- an email address

You can put a name in front of a receiver, e.g. `Max Muster - ABCD1234`.

### Notifications

Create a Notification and set **Channel** to "Threema". Receivers can be:

- a Phone or Mobile field of the document or of one of its child tables
- `owner`, the user who created the document
- a role; every user with that role is a receiver

For `owner` and roles, the app uses the **Mobile No** of the user. The message is a Jinja template, e.g. `Sales Order {{ doc.name }} was submitted`.

If sending fails, the document is still saved and the error goes to the Error Log.

### Threema Message Log

Every message the gateway accepted is listed in **Threema Message Log**. Rejected receivers and invalid entries are recorded in the Error Log.

## Development

```bash
cd apps/frappe_threema
pre-commit install
bench --site $SITE set-config allow_tests true
bench --site $SITE run-tests --app frappe_threema
```

## License

MIT, see [LICENSE](LICENSE).
