---
title: Threema-Benachrichtigung einrichten
audience: admin
requires: []
covers:
  - js:frappe_threema/threema/doctype/notification/notification.js
  - file:frappe_threema/threema/doctype/notification/notification.py
owner: tbd
order: 20
---

Mit einer Benachrichtigung im Kanal «Threema» sendet das System automatisch eine Threema-Nachricht, wenn bei einem Beleg etwas passiert. Ein Beispiel: Der Verantwortliche erhält eine Nachricht, sobald ein Auftrag gebucht ist.

![Benachrichtigung mit dem Kanal Threema und einem Empfänger](images/threema-benachrichtigung.webp)

## Voraussetzungen

- Sie haben die Rolle «System Manager».
- Die «Threema-Einstellungen» sind ausgefüllt.
- Jeder Empfänger hat seine Mobilfunknummer in der Threema-App verknüpft.
- Für Empfänger nach Rolle oder für den Ersteller des Belegs: Im Benutzer ist das Feld «Mobilfunknummer» ausgefüllt, im internationalen Format ohne «+».

## Vorgehen

1. Öffnen Sie eine neue Benachrichtigung unter `/desk/notification/new`.
2. Wählen Sie im Feld «Kanal» den Wert «Threema».
3. Wählen Sie im Feld «Dokumententyp» den Belegtyp, zum Beispiel «Auftrag».
4. Wählen Sie im Feld «Benachrichtigung senden bei» das Ereignis, zum Beispiel «Buchen».
5. Klicken Sie in der Tabelle «Empfänger» auf «Zeile hinzufügen».
6. Wählen Sie die Empfänger auf eine dieser Arten:
   - Im Feld «Empfänger nach Dokumentfeld» ein Telefon- oder Mobilfunkfeld des Belegs.
   - Im Feld «Empfänger nach Dokumentfeld» den Wert `owner`. Das System nimmt die Mobilfunknummer des Benutzers, der den Beleg erstellt hat.
   - Im Feld «Empfänger nach Rolle» eine Rolle. Das System nimmt die Mobilfunknummern aller Benutzer mit dieser Rolle.
7. Schreiben Sie den Text in das Feld «Nachricht». Sie können Werte des Belegs einsetzen, zum Beispiel `{{ doc.name }}`.
8. Prüfen Sie, dass «Aktiviert» gesetzt ist.
9. Klicken Sie auf «Speichern».

## Ergebnis

Bei jedem passenden Ereignis sendet das System die Nachricht an alle Empfänger. Jede gesendete Nachricht steht im «Threema-Nachrichtenprotokoll» unter `/desk/threema-message-log`.

Wenn das Senden scheitert, bleibt der Beleg trotzdem gespeichert. Der Fehler steht im «Fehlerprotokoll».

## Häufige Fehler

Im Feld «Empfänger nach Dokumentfeld» fehlt das gewünschte Feld: Die Liste zeigt nur Felder vom Typ Telefon oder Mobilfunk. Ein normales Textfeld mit einer Nummer erscheint nicht.

Ein Empfänger erhält nichts: Seine Nummer ist im Benutzer oder im Beleg nicht im internationalen Format erfasst, oder er hat sie in der Threema-App nicht verknüpft.

## Weitere Informationen

- [Threema-Nachricht senden](nachricht-senden.md)
- [Benachrichtigungen in der Frappe-Dokumentation](https://docs.frappe.io/framework/user/en/desk/notifications)
