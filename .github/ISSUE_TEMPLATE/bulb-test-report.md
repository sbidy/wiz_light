---
name: Bulb Test Report
about: If you have tested a Bulb with this integration.
title: "[Bulb Test Report]"
labels: enhancement
assignees: sbidy

---

**Please don't post bugs or issues here** This template is only for report a new bulb type for integration or successful test.

Provide the following information:

1. Made an UDP request with nc to the bulb:
`echo '{"method":"getSystemConfig","params":{}}' | nc -u -w 1 <YOU BULB IP> 38899`

2. Provide the native features of the bulb:
  - Dimmer (yes/no):
  - Color Temp (yes/no):
  - Effects (yes/no):
  - RGB (yes/no):

3. Tested?
    yes/no
    If you found bug or problems with the bulb please open an new issue and add a reference to this one.



**Additional Info**
Add any other useful information about the bulb? Purchase link? Other stuff you want to share?

**Thank you for your support** We will integrate the bulb as soon as possible.
