# Florida Triage Protocol

## Scope

This protocol details the steps taken to properly triage and schedule a patient with an acute issue.

---

## Surgical Check (Last 30 Days)

Before using the triage protocol, **ask if the patient had surgery in the last 30 days**:

- If **yes**, and they are an established patient who was referred to a surgeon by one of our providers:
  - They **must** be scheduled for a **same-day** appointment.
  - If no same-day slot is available, triage via **ICP** message to the **Patient Care Team**, mark it **URGENT**.
  - If the patient is **comanaged**, they should see their comanaging physician. If the patient requests a different provider, note it in the appointment details.

---

## Special Cases

- **ASC concerns**:
  - **Sarasota*: [SRQ-ASCinquiries@useye.com](mailto:SRQ-ASCinquiries@useye.com)
  - **Naples**: [Naples-ASCinquiries@useye.com](mailto:Naples-ASCinquiries@useye.com)
  - **Santa Fe (LEA)**: [santafeasc@useye.com](mailto:santafeasc@useye.com)
  - Refer to "Handling Patient Questions & Requests Protocol" for further instructions.
- **Dermatology concerns**: email [Derm@centerforsight.net](mailto:Derm@centerforsight.net) with the patient's name, DOB, phone number, and symptoms.

---

## Identify Urgency & Scheduling Process

1. Ask about the **symptoms**.
2. Ask about the **duration** of these symptoms.
3. **Determine the urgency** (Emergency, Urgent, or Non-Urgent) via the table below.
4. Document all symptoms, which eye(s) they affect, and how long they've been present.

---

## Emergency – Same Day (See ASAP)

- **New Patient**: Schedule with an **OD**.
- **Established Patient**: Schedule with their **primary provider**.
- If they are in a **post-op period** and **comanaged**, they should see their comanaging provider.

**Process**

- PAC schedules the **first available** opening (same day).
- If no ER or short appointment slot is open, you may schedule in any open space (excluding lunch hour).
- **If** no same day spots are available for that provider, send an **ICP** communication to the Patient Care Team of that region and mark **urgent**.
- **Dr. Banker** (CFS): Triaged by an **OD first** for emergency appts. For retina emergency referrals (e.g. detachment or tear), send an ICP message to Dr. Banker's team marked **urgent**. **Do not schedule**.
- If it's **3:30 PM–5:00 PM**:
  - Attempt a warm transfer to the office.
  - If the office is unavailable, enter an **ICP** message to the Patient Care Team. The office will contact the patient directly to schedule.
- If uncertain or unable to schedule, **notify** the Patient Care Team in ICP (if new patient, see "ICP IntelleChart – New Patient Task" below).

---

## Urgent – 24–48 Hours

- **New Patient**: Schedule with **OD**.
- **Established Patient**: Schedule with **primary provider**.
- If in post-op/comanaged, see their comanaging provider if possible.

**Process**

- Schedule in the first available **orange ER spot** first.
- If unavailable orange ER spots, schedule for any 30 minute (long) spot that that provider has in next 48 hours.
- If unsure where to schedule, send **ICP** triage communication to the Patient Care Team in that region and mark **urgent**.

---

## Non-Urgent – Next Available

- **New Patient**: Schedule with **OD**.
- **Established Patient**: Schedule with **primary provider**. For more information about scheduling non-urgent established patients, see "Scheduling Established Patients".
- For post-op/comanaged, normal scheduling unless otherwise indicated.

**Process**

- Schedule the patient in the next available spot (within 2 weeks).
- If unsure or no spots are available, triage via ICP to the Patient Care Team in that region.

---

## Examples of Symptoms by Urgency

| Emergency (Same Day)                                                                                    | Urgent (24–48 hrs)                                         | Non-Urgent (Next Avail)                                             |
| ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------- |
| **Retinal Tear/Detachment (within 30 days)**                                                            | Progressively worsening eye pain for 1 week                | Mild ocular irritation/redness                                      |
| **Sudden painless loss of vision**                                                                      | Moderate redness/pain for 1 week                           | Floaters (unchanged, previously diagnosed)                          |
| **Sudden onset of floaters/flashes/veil/spider webs**                                                   | Sub-acute loss of vision over a few days to 1 week         | Eyes become tired and blur after reading; trouble seeing road signs |
| **Sudden distortion/change on Amsler Grid**                                                             | Sudden onset of double vision                              | Difficulty with near/fine print                                     |
| **Foreign body (something in eye)**                                                                     | Ocular discharge (clear, milky, watery)                    | Lid twitching                                                       |
| **Chemicals in eye** (flush at urgent care/hospital until pH = 7, then clinic)                          | Severe photophobia (with/without pain)                     | Mucous discharge                                                    |
| **Acute, rapid onset eye pain/discomfort**                                                              | Loss of only pair of glasses/contacts needed for daily use | Tearing (no other symptoms)                                         |
| **Acute red eye w/ or w/out discharge**                                                                 |                                                            | Mild redness w/o other symptoms                                     |
| **Trauma to eye, head, face**                                                                           |                                                            |                                                                     |
| **Referral stating emergent situation**                                                                 |                                                            |                                                                     |

> **Note**: Sudden difficulty with distance/near vision should be treated as an emergency.

---

## Scheduling Instructions by Urgency

[Content repeated above – may remove if redundant.]

---

## ICP Triage Messages

If you need to **triage via ICP** instead of scheduling immediately, see the table for **notify** field groups:

- `*CFS North Region Patient Care Team`
- `*CFS Mid Region Patient Care Team`
- `*CFS South Region Patient Care Team`
- `*SFEC Patient Care Team`
- `*LEA Patient Care Team`
- `*RHC Patient Care Team`

**Add the provider's name at the beginning of the message** if known.  
Use **clear, concise language**—avoid abbreviations. Document eye(s) affected, symptom details, cause if known, and duration. Include the patient's preferred location and best callback number.  
Inform the patient that staff will call them to discuss their symptoms and urgency.

---

## ICP IntelleChart – New Patient Task

1. For a **new patient**, follow **NextGen Transfer to ICP** before creating an ICP task.
2. Create an ICP task:
   - **Notify →** "Practice Patient Care Team"
   - Mark **URGENT** if needed.
3. If the system doesn't show the user's initials in the ICP task, it means the patient is not linked to a practice.
   - In that case, schedule an appointment under **ICP resource** using the **Transfer to ICP** event to link them.

---

## Additional Reminders

1. If symptoms worsen before the scheduled appointment, advise the patient to **call back** immediately.
2. Explain to the patient that he/she will likely be dilated for an Emergency visit.
3. If the patient isn't being seen the same day but has any of the following, they'll be **dilated** at the visit:
   - Blurred Vision
   - Decrease in Vision
   - Double Vision
   - NEW Floaters
   - Curtain, Veil, or Spider webs

---
