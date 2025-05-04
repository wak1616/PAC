# 72-Hour Scheduling Rule – Quick Reference for Call Center Agents

## When to Use
Use this rule to override standard appointment templates if a patient needs to be scheduled within 72 hours from the call time (such as emergency cases).

## Allowed Overrides

- New patient → any New patient slot (Comp Medical – New, Routine Employee – New, or Routine Vision – New)
- Established patient → any New or Established patient slot (Comp Medical – New/Est, Routine Employee – Est, or Routine Vision – Est)

## Restrictions

- Do not schedule past 3:30 PM.  
- If after 3:30 PM, talk to your supervisor and/or send a message to the Patient Care Team of the location closest to the patient to have them scheduled.

## Doctors Included

### ODs / Optometrists

- **AEC:** N/A  
- **CEP:** N/A  
- **CFS:** Dr. Len Brown, Dr. Daniel Hadland, Dr. Melissa Hammond, Dr. Erin Hardie, Dr. George Hurwitz, Dr. Todd Lang, Dr. James Lenhart, Dr. Lori Long, Dr. Casey Maloney, Dr. Elizabeth McVey, Dr. David Mertzlufft, Dr. Bradley Middaugh, Dr. Patrick Nelson, Dr. Logan Page, Dr. Charles Putrino, Dr. Rachel Randolph, Dr. Kyle Schaub, Dr. Joseph Sowka, Dr. Scott Stevens, Dr. Hunter Vittone, Dr. Callista Wlaschin, Dr. Trisha Werner  
- **SFEC:** Dr. Sarah Johnson, Dr. Brian Marhue, Dr. Penny Orr, Dr. Hunter Vittone  
- **LEA:** Dr. Christine Bui, Dr. Mari Holderby, Dr. Alexandria Rawls  
- **GEC, KEC, RHC:** N/A

### MD / DO

- **LEA:** Dr. Jose Vazquez

## Color Key (as seen in NextGen)

### Light Green
- Comp Medical – New (Adult or Child)

### Yellow
- Comp Medical – Est (Adult or Child)  
- Routine Employee – New (Adult or Child)  
- Routine Employee – Est (Adult or Child)

### Dark Green
- Routine Vision – New (Adult or Child)  
- Routine Vision – Est (Adult or Child)

## Dilation and Exam Duration (inform patient clearly)

> "Your eyes will be dilated, causing blurry vision and light sensitivity for several hours. Please arrange transportation home."

> "Dilation can only be waived by a Physician."

> "Your exam may last approximately 90-120 minutes if a comprehensive exam is needed."

## Required Documentation

- Note “72-hour rule” clearly in appointment details.  
- Extend appointment from 15 to 30 min when combining short slots.

## Important Reminders

- Patients are typically only eligible through their vision plan once per year. If a routine exam is being scheduled before the 1-year eligibility timeframe, the patient may need to use their medical insurance instead.  
- Always schedule patients with both vision and medical insurance info.

## If Additional Requirements are Needed by Insurance

- If referral is required but not obtained, inform patient of self-pay requirement:

> "Your insurance requires a referral from your Primary Care Provider (PCP). It usually takes about seven business days. Without this referral, you can be seen as self-pay. You’ll sign a Self-Pay form, and fees will be due at visit."

- Document PCP information clearly in the patient’s chart and appointment notes.  
- Note in the appointment details: “Pt is aware PCP referral is required; self-pay if not received.”
- This also applies to Optum VA insurance patients if the authorization on file does not match the specific doctor being scheduled under the 72-hour rule. Inform the patient:

> "The current Optum VA authorization is for Dr. `{{current_provider_name}}`.  
> If you are requesting a new appointment with a different provider, we must submit a request for additional services.  
> This process can take up to seven (7) days to receive VA approval.  
> If there is no VA authorization on file, you have the option to bill your medical insurance instead."

## Closing Scripting

- Confirm appointment details: date, time, and location.  
- Inform patient about pre-visit registration via Phreesia:

> "You may receive a Phreesia registration message. Please complete this in advance to streamline your check-in. Contact us if you have questions."

- Final confirmation:

> "Thank you, [Mr./Ms. Patient Last Name]. Can we assist you with anything else? We look forward to seeing you on [date] at [time] at our [location] office."
