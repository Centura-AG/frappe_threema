---
title: Threema-Nachricht senden
audience: admin
requires: []
covers:
  - doctype:Threema Center
  - doctype:Threema Message Log
owner: tbd
order: 10
---

Im Threema-Zentrum senden Sie eine Nachricht von Hand an eine oder mehrere Personen. Sie brauchen das zum Beispiel für eine kurzfristige Information an ein Team.

![Threema-Zentrum mit Empfängerliste und Nachricht](images/threema-zentrum.webp)

## Voraussetzungen

- Sie haben die Rolle «System Manager».
- Die «Threema-Einstellungen» sind ausgefüllt: «Gateway-URL», «From» (die Gateway-ID) und «Geheimnis».

## Vorgehen

1. Öffnen Sie das «Threema-Zentrum» unter `/desk/threema-center`.
2. Tragen Sie im Feld «Empfängerliste» die Empfänger ein, einen pro Zeile. Ein Empfänger ist eine Threema-ID mit 8 Zeichen, eine Mobilfunknummer im internationalen Format ohne «+», zum Beispiel `41791234567`, oder eine E-Mail-Adresse.
3. Schreiben Sie den Text in das Feld «Nachricht».
4. Klicken Sie auf «Nachricht senden».

## Ergebnis

Das System sendet die Nachricht an jeden Empfänger einzeln. Die Meldung «Threema-Nachricht gesendet an: …» nennt die Empfänger, an die das Gateway die Nachricht angenommen hat.

Jede gesendete Nachricht steht im «Threema-Nachrichtenprotokoll» unter `/desk/threema-message-log`, mit «Absender», «Empfänger» und «Gesendet am».

Bei einer Mobilfunknummer oder E-Mail-Adresse findet das Gateway die Threema-ID nur, wenn der Empfänger seine Nummer oder Adresse in der Threema-App verknüpft hat.

## Häufige Fehler

«Bitte geben Sie gültige Threema-Nummern ein»: Die Empfängerliste ist leer oder enthält nur Leerzeichen. Tragen Sie mindestens einen Empfänger ein.

Ein Empfänger fehlt in der Meldung: Das Gateway hat die Nachricht für diesen Empfänger abgelehnt, oder der Eintrag ist keine gültige Threema-ID, Nummer oder Adresse. Die Ursache steht im «Fehlerprotokoll».

## Weitere Informationen

- [Threema-Benachrichtigung einrichten](benachrichtigung-einrichten.md)
- [Threema Gateway](https://gateway.threema.ch/de/)
