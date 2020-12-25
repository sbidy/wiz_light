---
name: Bulb Test Report
about: Please use this template to report a bulb you have tested with this integration.
title: "Bulb Implementation Report"
labels: "Bulb - Implementation Open" 
assignees: sbidy

---

**Please don't post bugs or issues here** This template is only for report a new bulb type for integration or successful test.

Provide the following information:

**1. Made an UDP request with `nc` to the bulb:**
`echo '{"method":"getSystemConfig","params":{}}' | nc -u -w 1 <YOU BULB IP> 38899`
Report the output here:


**2. Provide the native features of the bulb:**
  - Dimmer (yes/no):
  - Color Temp (yes/no):
  - Effects (yes/no):
  - RGB (yes/no):


**3. Tested?**
    yes/no
    If you found bug or problems with the bulb please open an new issue and add a reference to this one.


**OPTIONAL**

**4. Prepare the YAML - replace `<Name>` with the ESP_XXXXXXXX name from step 1.**
  ```
    <Name>:
       name: <Name>
       features:
         brightness: true / false
         color: true / false
         effect: true / false
         color_tmp: true / false
       kelvin_range:
         min: 2200 / or other?
         max: 6500 / or other?
   ```

**Additional Info**
Add any other useful information about the bulb? Purchase link? Other stuff you want to share?

**Thank you for your support**

We will integrate the bulb as soon as possible.
