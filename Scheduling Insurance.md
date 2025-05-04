# Scheduling Reference – Insurance

> **Scope:** This protocol explains how to collect, verify, and enter patient insurance information in NextGen Practice Management (PM).

---

## Overview

When a patient contacts the office to schedule any appointment, staff must:
1. Confirm the patient's **demographic and insurance** information.
2. Verify the **plan name** and **policy number** to ensure the insurance on file is active.
3. **Arrange** insurance policies in the correct order in NextGen:
   1. **Primary** Medical Insurance
   2. **Secondary** Medical Insurance
   3. **Tertiary** Medical Insurance
   4. **Vision** Insurance

> **Note:** Vision plans **cannot** be used for medical exams (cataract, cornea, glaucoma, LASIK consultations).

If the patient has **no medical insurance**, set them as **Self-Pay – No Insurance**.

Use the **US Eye Insurance Guide** to confirm whether the plan is in-network, out-of-network, or non-participating.

---

## Collecting & Entering Insurance

### 1. Verify Information
- Ask if the patient has their **primary insurance card** available.
- **Questions**:
  1. "What is the plan name on your insurance card?"
  2. "Is this a **Commercial, Medicare, or Medicaid** plan?"
     - **Note**: Supplement/Medigap can **only** be secondary.
  3. "Does your insurance card say **PPO** or **HMO**?"

> **If the patient cannot provide accurate insurance info**, inform them that you **cannot schedule** until you have their plan details. Offer to wait while they retrieve the cards or to have them call back.

### 2. Insurance Guide Check
1. **Confirm** whether the practice participates with the plan (in-network vs. out-of-network vs. non-participating).
2. If **in-network** and no additional action is needed, **enter** the plan in NextGen and continue scheduling.
3. If **in-network** but requires a **referral**, schedule the patient **7–14 days** out to allow time for referral.
   - For emergent appointments, inform the patient that if the referral is not received in time, they will be **self-pay** at time of service.
   - If patient agrees to proceed, enter **Self-Pay – Do Not Bill Medical Ins** in the policy number field (e.g., "ER APPT"), with effective and expiration date set to the day of service.
   - Email **Insurance Verification** to notify them of the urgent need for a referral (include plan name, policy #, patient details, date).

4. If **VA (Optum)** coverage:
   - **VA must schedule** the appointment directly (patient cannot self-schedule).
   - Check the **Authorization** tab in Insurance Maintenance for an existing authorization.
   - If no authorization, let the patient know the VA needs to send a new one.

5. If the patient's plan is **non-participating** (or the patient does not want to use insurance), explain they will be **self-pay**:
   - A **self-pay deposit** is collected at check-in, additional costs at check-out.
   - Enter as **Self-Pay – No Insurance**, **Self-Pay – Non Par With Ins**, or **Self-Pay – Do Not Bill Medical Ins**, as appropriate.
   - See *RCM Procedure Manual Self-Pay Deposit Collection* for pricing estimates.

### 3. Ask About Secondary Insurance
1. Collect the **secondary plan** name, plan type (Commercial/Medicare/Medicaid), and "PPO" or "HMO" status.
2. Check the **US Eye Insurance Guide** for participation status.
   - If **in-network** for secondary, enter it in PM and finalize scheduling.
   - If **out-of-network**:
     - Inform patient their copay/out-of-pocket may be higher.  
     - Note in appointment details: "Patient made aware on [date] we are OON with higher OOP costs."
   - If **no OON** benefits:
     - Patient must proceed as self-pay. Load their insurance as **Self Pay – Non Par With Ins** and enter the plan name in the Policy Number field.

### 4. Deactivating Old Plans
- If you added a **new insurance** to an existing chart, check whether any prior plans are now inactive.
- If so, add an **expiration date** and remove the **Active** marker. (See *NG PM – Deactivate an Insurance*.)

---

## Sample Scripting

> **Confirming Information**:  
> "Can you please confirm your full name, date of birth, insurance plan, and insurance ID number so I can verify we have the most updated billing information on file?"

> **Patient Only Has Vision Plan**:  
> "Please note that vision plans cannot be used for medical exams such as cataracts, cornea, glaucoma, or LASIK consultations."

> **Cannot Provide Insurance**:  
> "In order to proceed with scheduling, it's important we have accurate insurance info to ensure coverage. If you cannot provide it now, please call back when you have it so we can schedule your appointment."

> **Emergent Appointment, Referral Required**:  
> "Your insurance plan needs a referral from your PCP. We will request an urgent referral, but if it isn't received before your appointment, you'll be considered self-pay at time of service. All fees will be due at check-in. Would you like to proceed?"

> **Non-Participating Insurance**:  
> "We are not in-network for your plan. You can still be seen on a self-pay basis. All payments are due at time of service."

---

## References
- **US Eye Insurance Guide** (in-network vs. out-of-network / non-participating)
- **NG PM – Deactivate an Insurance**
- **RCM Procedure Manual: Self-Pay Deposit Collection** 