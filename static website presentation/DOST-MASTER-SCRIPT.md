# FALCON-01 — DOST Master Script
**Plain-English delivery script · 15 chapters · 6 October 2026**
**Project FALCON-01 · Phase 1 Undergraduate Prototype · Fullbright College**

This is the master script. You can read every line out loud, as it is.

**Short sentences on purpose.** One idea per sentence. If you get lost, stop. Look at the
screen. Start the next sentence.

---

## Before you start

- Open **`present.html`**, not `index.html`.
- Bright room or weak projector? Use **`present.html?big=1`**.
- Keys: `Space` or `→` next · `←` back · `L` chapters · `P` presenter mode · `Esc` exit.
- **Say this out loud four times:** *"simulated, not validated."*
  Say it in chapters 05, 07, 08, and 10.

**Your one main sentence. Use it in the opening and again at the end:**
> *"Affordable, documented, and easy to check. We are putting existing parts together well.
> We are not inventing a new sensor."*

---

## Timing

| Block | Chapters | 15 min | 20 min | 25 min |
|---|---|---|---|---|
| Opening and objectives | 00–01 | 2.0 | 3.0 | 3.5 |
| The system, buoy to shore | 02–06 | 5.0 | 7.0 | 8.5 |
| Evidence and limits | 07–11 | 4.0 | 5.0 | 6.5 |
| Plan, cost, the ask | 12–14 | 4.0 | 5.0 | 6.5 |
| **Total** | | **15.0** | **20.0** | **25.0** |

### If you are running short

Stop at these three, in this order.

| Order | Chapter | Saves | What to do |
|---|---|---|---|
| 1 | 04 — ESP32 | ~1 min | Say one line only. Skip the diagram. |
| 2 | 07 — Wave estimate | ~1 min | Just point. Do not click. |
| 3 | 09 — Dashboard | ~0.5 min | Name the four tabs. Do not click. |

### If you have extra time

| Order | Chapter | Adds | What to do |
|---|---|---|---|
| 1 | 05 — LoRa | ~0.5 min | Run the break-and-recover demo twice |
| 2 | 08 — AI | ~0.5 min | Explain the baseline properly |

**Page 16 (Finale animation) sits outside the timed talk:** after the ask, step onto it and let the 3D flight loop behind questions — or skip it if time is short.

**Never cut 05, 08, 10, 12, or 13.** Those carry the demo, the honesty, the plan, and the cost.

---

# THE SCRIPT

## 00 — THE OCEAN · 1.5 min
**On screen (first):** Cover — title, FALCON acronym, team, school · **Click:** `Start the presentation ↓`
**On screen (second):** Hero + problem · **Click:** `Begin the journey ↓`

> "Good morning. Thank you for having us.
>
> My name is [your name]. I am from the FALCON Research Group. BS Information Technology,
> Fullbright College. With me are [names of teammates present].
>
> Our advisers are Sir Jam on the papers and Sir Jeff on the hardware."
>
> Let me start with a question.
>
> How many of you made a decision this month about the sea? Going out to fish. Sending a boat.
> Bringing one home.
>
> Every barangay on this coast makes decisions like that. They are all made close to the water.
>
> And almost none of them have a real number to go with it.
>
> Commercial wave buoys do exist. But they cost a lot. They are closed systems. And they are
> hard to maintain.
>
> So for most coastal communities, the answer to 'what is the sea doing right now' is nothing.
> No data at all.
>
> That is the gap we want to help close.
>
> FALCON-01 is our answer. One solar buoy out at sea. One station on shore. The buoy listens.
> The shore does the thinking.
>
> And we built it so a local person can understand it, check it, and fix it themselves."

**If they interrupt you:** *"A buoy is just a floating sensor box. The heavy work happens on shore."*

---

## 01 — OBJECTIVES · 1.5 min
**On screen:** The six objectives

> "Let me be clear about what this project is. And what it is not.
>
> **Phase 1 is about putting things together and testing them. It is not about inventing.**
>
> We did not invent a sensor. We did not invent a buoy. We did not invent an AI algorithm.
> All of that already exists.
>
> What does not exist is a cheap, well-documented, honestly-tested version of it.
> Built for a community setting.
>
> That is what we made. Here are our six goals.
>
> **One.** A solar buoy that a student can open and repair.
>
> **Two.** Measure pressure and wind. Also track position, time, power, and security.
>
> **Three.** Estimate wave height from that pressure. And calibrate it properly.
>
> I want to stress the word *calibrated*. An uncalibrated wave number is just a guess.
>
> **Four.** Send everything to shore by LoRa. Store it. Show it on a dashboard.
>
> **Five.** Test the whole thing honestly. Accuracy. Reliability. Delay. Power. Ease of use.
>
> **Six.** Try short-term AI wave prediction. And compare it against a simple baseline.
>
> That last one is the most important sentence I will say today. **We check the numbers before
> we believe them.** Everything else follows from that."

**Do not give any accuracy number in this chapter.**

---

## 02 — FALCON BUOY · 2 min · demo
**On screen:** 3D buoy · **Demo:** click the pressure sensor, read the panel, go back

> "This is FALCON-01.
>
> Let me walk you around it.
>
> **On the buoy:** an ESP32 controller. An underwater pressure sensor — that is our main wave
> signal. Wind speed and direction sensors. GPS — it does three jobs. It tells us where the buoy
> is. It gives us a clock. And it sets a boundary, so we know if the buoy gets dragged away.
>
> A battery and solar panels for power. And a LoRa radio to talk to shore.
>
> **On shore:** a small computer called the Bay Station.
>
> Now here is the decision I want you to remember.
>
> There is **no computer on the buoy. No cellular on the buoy.** Nothing at sea does heavy work.
>
> The buoy only senses, times, checks, and sends. All the real processing happens on shore.
> Where there is electricity. Where there is storage. Where a person can fix it.
>
> And every part was chosen for one reason: **a student can buy it, wire it, document it, and
> repair it.**
>
> Not the cheapest part on a website. The part we can actually buy here, actually solder, and
> actually explain in a thesis."

**Demo:** *"Here is the pressure sensor."* — click it, read the panel, go back.

**If asked about the model:** *"The old CAD file still has old antenna names and an Orange Pi
shape in it. Those are not our current parts. We kept the original file rather than invent a
layout. The new design is still being drawn."*

---

## 03 — SENSORS · 1 min
**On screen:** Sensor menu · **Demo:** click pressure, then click wind

> "We use two main sensors.
>
> **Pressure.** It sits under the water. This is our raw signal for waves.
>
> **Wind speed and direction.** This matters a lot for anyone deciding to go out on the water.
>
> We also track position, power, and security. These support the main two. They tell us where
> the buoy is, how much battery is left, and whether anyone has opened it.
>
> Now, what we left out on purpose: water temperature and salinity.
>
> We could add them. We did not. We kept Phase 1 small enough to finish and test properly.
> Saying no to things is part of the work."

---

## 04 — ESP32 SOFTWARE · 1.5 min · cut first
**On screen:** Chip diagram and the data frame · **No clicking needed**

> "This is the software that turns raw signals into useful information.
>
> The ESP32 sits in the middle. Four things come in at once: pressure, wind, GPS, and power
> with security.
>
> It reads all four. It stamps the time. It checks each value. And it packs everything into one
> clean frame.
>
> That frame goes out every **4.8 seconds**.
>
> But here is what I want you to notice. Each reading carries a **quality flag**.
>
> If a reading fails the check, we do not hide it. We mark it, and we send it anyway with the
> mark on it.
>
> We do not drop it. And we do not smooth it into looking fine.
>
> That is a small decision with a big result. Six months from now, if someone asks 'why was this
> reading wrong in June,' the answer is written in the data.
>
> **An archive that hides its own mistakes is not evidence. It is decoration.**"

**If you cut this chapter, say only:**
> "A small controller reads the sensors, checks the values, and packs one frame every 4.8 seconds."

---

## 05 — THE LoRa LINK · 2 min · demo
**On screen:** The signal path and six steps · **Demo:** click `Interrupt LoRa`, then `Restore LoRa`

> "This is the link between buoy and shore. And I want to actually break it in front of you.
>
> Normally the buoy senses, packs a frame, sends it by LoRa, and the shore receives it.
>
> Two things to notice. LoRa sends small packets over long distance. That is what it is for.
>
> And the buoy never touches the internet. The SIM, the 4G, the 5G — all of that stays on
> shore, where there is power and signal.
>
> The six steps are: sense, frame, cross, buffer, receive, insight.
>
> Now. What happens when the link fails?" **— click `Interrupt LoRa` —**
>
> "The sending stops. The shore goes quiet.
>
> And here is the important part. **The buoy does not stop.** It keeps sensing. It saves every
> frame it could not send. And it saves them **with the original time stamp.**
>
> Not the time they finally got through. The time they were actually measured." **— click `Restore LoRa` —**
>
> "The link comes back. It replays them, in order, with the right times.
>
> And watch the duplicates. When a frame arrives that we already have, **we reject it.**
>
> The worst thing a data archive can do is count the same wave twice.
>
> That is small engineering. But it is the difference between a demo and something a community
> can trust."

**Say this right after. Do not skip it.**
> "Now the honest part. **This is simulated.** We have not picked the LoRa hardware yet. The
> legal band is not confirmed. We have not measured coverage out there.
>
> **So there is no range guarantee.** What you saw is our design working. The real range test is
> Gate 03 and Gate 04."

---

## 06 — THE BAY STATION · 1.5 min · demo
**On screen:** The shore pipeline · **Demo:** open `Inspect the Bay Station`, click two stages, exit

> "Everything arrives here.
>
> **One** computer on shore does all of it. It receives the radio signal. It checks each frame.
> It stores everything. It runs the wave calculation. It runs the AI. And it shows the
> dashboard.
>
> One computer. That is on purpose. One thing to maintain. One thing to power. One thing to
> secure.
>
> And the internet connection stays here on shore, not out at sea.
>
> Three words for this stage: **receive, process, insight.**
>
> One more thing. Every reading comes with a label. **Live, simulated, or estimated.**
>
> If a number is simulated, it says simulated. If it is an estimate, it says estimated.
>
> We did not want a screen where a visitor cannot tell what is real."

**Demo:** click two stages — *"This is the radio that picks up the signal. And this is where the
forecast is made."*

---

## 07 — WAVE ESTIMATION · 1 min · cut second
**On screen:** Raw pressure to estimate · **Demo:** click 01, 02, 03. **If cutting, just point.**

> "Pressure goes in. Estimated wave height comes out. But there is a method in between.
> And the method is the honest part of this slide.
>
> The steps are: check the data, filter it, remove the baseline, correct for depth, calibrate,
> then estimate the wave height.
>
> Let me explain two of those.
>
> **Removing the baseline.** The tide goes up and down over hours. That is not a wave. If we do
> not subtract it, our system is really just a tide detector.
>
> **Depth correction.** Our sensor is not at the surface. It sits under the water. What it
> feels is the pressure change the wave makes down there. Ignore the depth and you get a number
> that is confidently wrong.
>
> Now the limit. **This is an illustration only.**
>
> We have not finished the depth correction. We have not calibrated it. We have not compared it
> to a real reference instrument.
>
> **So there are no metres in this project yet. These are relative units.**
>
> We are showing you the shape of the method. Not a result."

---

## 08 — AI PREDICTION · 1.5 min · explanation, no demo
**On screen:** 4 plain-English steps: where data comes from → how it predicts → safety limits → how it is judged · **No clicking — explain only**

> "The goal is to predict waves five, ten, and fifteen minutes ahead.
>
> Here is where we actually are. **Today it is a simple trend line. It is not a trained model.**
>
> Walk the four cards with me.
>
> **One — where the data comes from.** The shore computer stores every reading. The predictor looks at the last 120 wave-height records, and waits until there are enough samples to trust.
>
> **Two — how it predicts.** It draws a straight line through the recent history and extends it 5, 10 and 15 minutes ahead. Distant predictions are shrunk on purpose — the further out, the less sure.
>
> **Three — safety limits.** Changes are capped and clamped so one noisy reading cannot spike the forecast. Each prediction shows a confidence level, and the sea reads CALM, MODERATE or ROUGH.
>
> **Four — how it is judged.** The model must beat the simplest baseline — assume nothing changed — on real held-out data, measured with MAE, RMSE and bias. Until it does, it is a demo.
>
> That baseline has a name: **persistence.** Tomorrow looks like today. It is embarrassingly hard to beat, which is exactly why we use it.
>
> **Accuracy and skill are still unvalidated.** I will not tell you this is accurate. We do not know yet."

---

## 09 — DASHBOARD · 1 min · live demo
**On screen:** the live edge dashboard inside the page · **Needs:** edge service running before you present · **Backup:** static snapshot shows automatically if offline

> "This is not a picture of our dashboard. **This is the dashboard.**
>
> Running on this machine right now is our shore computer software — the
> edge service. It stores the readings, runs the wave calculation, and
> serves exactly what you see here.
>
> **Overview** — estimated wave height, AI prediction, sea condition, wind,
> pressure, battery, solar, GPS, enclosure. Every number carries its label:
> simulated, estimated, or live.
>
> **Sensors, Buoy Motion, GPS, Logs and Alerts, Settings** — click through
> them. This is the operator's actual working screen, not a mock.
>
> There are four security states: secure, warning, alert, and disarmed.
>
> But here is the rule that matters. **Normal wave motion must not raise an alert.**
>
> A buoy on a rough sea is doing its job. It is not reporting a break-in.
>
> So before we claim any alarm works, **we have to test it staying quiet.**"

**Before presenting, in a terminal next to the browser:**
> `cd edge && python3 -m falcon_edge.service` → dashboard at `http://127.0.0.1:8765/`.
> If the live view shows OFFLINE, press Retry after starting the service — a
> static snapshot stays on screen until then, so the chapter is never blank.
> There are four security states: secure, warning, alert, and disarmed.
>
> But here is the rule that matters. **Normal wave motion must not raise an alert.**
>
> A buoy on a rough sea is doing its job. It is not reporting a break-in.
>
> If we ship an alarm that goes off every time the weather is bad, people will switch it off.
> Then it protects nobody.
>
> So before we claim any alarm works, **we have to test it staying quiet.**
>
> A system that cannot stay quiet when it should is not a working alarm."
>
> "Also, see `SIMULATED PREVIEW` at the top. This screen is a picture of our interface.
> **There is no live connection.**"

---

## 10 — VALIDATION & STATUS · 1.5 min · the honest chapter
**On screen:** The test plan, and the two columns

> "This is the chapter I care most about. So I will be blunt.
>
> **Nothing here is validated yet.**
>
> Every measurement has a test it must pass before we are allowed to give it a number.
>
> Here is that list. Bench tests on each sensor. Pressure against a reference. Wind against a
> reference anemometer. GPS boundary. Vibration and tamper. Power budget.
>
> Plus: radio loss, delay, range, and buffering. Dashboard use on a phone and a laptop. And the
> AI, measured against persistence.
>
> Now I want to be careful about one word. People use it loosely.
>
> **Implemented means the software runs. It does not mean the measurement is accurate.**
>
> Those are two completely different claims. Many prototypes blur them. We try not to."
>
> **— point to the columns —**
>
> "**Built and running:** the firmware shell and its setup page. The data frame with its quality
> flags. The shore service — simulator, database, API, dashboard. The wave calculation. The GPS
> boundary check.
>
> **Not yet proven:** the final sensor calibration. Real GPS and tamper performance. Real radio
> hardware and its range. A field-trained AI model."
>
> **— slow down —**
> "We would rather show you an honest prototype than an impressive claim."

---

## 11 — SCOPE & RISKS · 1 min · the safety chapter
**On screen:** The "does not do" list, and the risk table

> "Let me tell you what this system **does not do.** I think this matters more than what it does.
>
> It does not predict tsunamis.
> It does not predict typhoons.
> It does not give official warnings.
> It does not control boats.
> It is not a lab water quality kit.
>
> **This is not an official warning system. It does not replace any government monitoring.**
>
> If anyone leaves here thinking this is a warning system, we failed. No matter how good the
> code is.
>
> Now the risks. And what we do about each.
>
> **Power.** We measure the real usage. We do not guess.
> **Water and rust.** We test on a bench first. Then we deploy slowly. Not one big ocean launch.
> **Radio range.** We run a real range test before we claim anything.
> **Calibration drift.** We have a written routine, and we compare against a reference.
> **False alarms.** We test that it stays quiet before we trust it.
>
> Every risk has a named fix. None of them is 'we will deal with it later.'"

---

## 12 — ROADMAP & TEAM · 2 min · the setup for the ask
**On screen:** The five gates and the team · **Demo:** click each gate

> "Let me show you how the money gets spent. Because this is **not a shopping list.**
>
> We are asking for a **five-month, twenty-week bootcamp.** Each stage produces what the next
> stage needs.
>
> **Gate 01. Month 1. Freeze and buy.** Parts list locked. Hardware ordered. Permits filed.
> What can we claim after this? **Nothing.** Buying a sensor does not tell you if it works.
>
> **Gate 02. Month 2. Bench testing.** One sensor at a time. ESP32, then pressure, then wind,
> then the rest. Rails and protection checked. After this we can say it runs on a bench. Nothing
> more.
>
> **Gate 03. Month 3. Calibrate and build software.** Pressure calibration. Wind calibration. The
> database. The API. The shore radio and its SIM. And recovery when the signal drops. After
> this we can say our readings are corrected against a reference. Still no sea data.
>
> **Gate 04. Month 4. Controlled testing.** This is the one that matters. Tank or pool, against
> a real reference. MAE, RMSE, bias. False alarm tests. A full day of power. Three days of solar.
> Waterproofing.
>
> I want to say this clearly: **no accuracy number leaves this gate.** If the numbers are bad,
> we report bad numbers.
>
> **Gate 05. Month 5. Sea trial and thesis.** A supervised pilot. The AI against persistence, on
> data it has not seen. Updated drawings and limits. The final report.
>
> After this gate we claim **only what the earlier gates actually measured.**
>
> Now the team. Four students. The split is already fixed.
>
> **Jhon Ruzzel Correa** — hardware, power, radio firmware.
> **Gwyn Isabel Enriquez** — the shore computer, the AI, the dashboard.
> **Mayla Bacaltos** and **Gina Caballero** — the thesis and the test records.
>
> Two advisers. **Sir Jam** on the papers. **Sir Jeff** on the hardware.
>
> And we have a third seat empty. For a software or AI mentor. That seat is part of our ask.
>
> The plan is a bootcamp dorm. Half on-the-job training, half thesis. DOST hosts the OJT.
> Mornings for OJT work. Afternoons for the thesis. Saturday for building. Sunday for writing
> and rest.
>
> **Five months is our real estimate. Four months is the stretch goal.**"

---

## 13 — IMPACT & FUNDING · 2 min · the number
**On screen:** Who it serves, and the cost table · **Demo:** click the filter buttons

> "Let me be honest about who this serves.
>
> The first trial should fix **one real problem for one real user.** Not everyone at once.
>
> Coastal towns and disaster offices want a local record, for planning and drills.
> Fisherfolk want simple information they can actually reach.
> Schools and researchers want something they can build on and check.
> Ports and tourism want to know the equipment is working.
>
> Every card on that screen ends with the same words: **still to confirm.**
>
> No site is chosen. No user is confirmed. I will not stand here and pretend otherwise.
> We are asking you to help us confirm the first one properly."
>
> **— point to the innovation note —**
>
> "Let me be clear about **where the innovation is.** This question always comes up.
>
> Our contribution is putting established parts together cheaply. And testing them honestly.
> Documented, so others can repeat it.
>
> **We did not invent a sensor, a buoy, or an AI algorithm.**
>
> I think that is a strength. It means someone else can build it too."
>
> **— filter the table —**
>
> "On cost. The range is **₱90,000 to ₱150,000.** The middle, about **₱115,000,** covers shipping
> and tax, one calibration session, and spare parts.
>
> **These are planning numbers. They are not quotes.** Before we submit, every line gets a real
> price from three suppliers. I will not give you a final peso figure until we have done that."
>
> "The seven lines: sensors and electronics, ₱18,000 to ₱26,000. Shore computer, radio, and SIM,
> ₱15,000 to ₱25,000. Solar, battery, and controller, ₱14,000 to ₱22,000. Buoy body and
> enclosure, ₱15,000 to ₱25,000. Mooring, ₱7,000 to ₱14,000. Calibration and trials,
> ₱12,000 to ₱20,000. Transport, spares, and backup, ₱9,000 to ₱18,000.
>
> **What you get:** one working, documented prototype. Calibrated sensors. A dashboard and a
> data archive. Real sea test results. A fair test of the AI. And documents and data other
> researchers can reuse."

---

## 14 — CLOSE · 1 min · the ask
**On screen:** closing slide + WATCH IT WORK loop · **Static ang 14–15; mag-scroll sa page 16 — flight plays ONCE from the buoy (~30s: buoy → rise → line → receiver → INSIDE Bay Station, then holds) · umalis/bumalik = replay from buoy** · Speak the 5-point ask over the flight

> "Let me finish with what happens next.
>
> Lock the parts list. Build the pressure system. Calibrate it. Connect the buoy radio to the
> shore radio. And gather **real reference data before we make any performance claim.**
>
> So, what are we asking for? Five things.
>
> **One.** Accept this as a **DOST on-the-job training placement.** Half OJT, half thesis. So the
> work continues on a schedule instead of stopping when the semester ends.
>
> **Two.** A **mentor.** One person for software or AI, and the third adviser seat.
>
> **Three.** **Help buying and building** the parts, in that ₱90,000 to ₱150,000 range.
>
> **Four.** **Access to calibration and a site.** A reference instrument, and permission for a
> supervised tank or pool test.
>
> **Five.** **Support for the sea trial, and shared ownership of the data.**
>
> Let me be clear about what that last one means.
>
> **We are not asking you to trust an untested forecast.** We are asking for the chance to
> produce real evidence. One number that a barangay here can use, and can defend, because we
> measured it here and wrote it down clearly enough for them to check our work.
>
> Thank you. **Project FALCON Research Group, BS Information Technology, Fullbright College.**"

---

# Q&A

About five minutes. **Questions 9, 10 and 11 decide the outcome.** Rehearse those out loud.
For everything else, a short honest answer beats a long one.

## The eight technical ones

**1. "Is it accurate?"**
> "Not yet. I will not give you a number. No accuracy claim leaves Gate 04. That is where we
> test against a real reference and report MAE, RMSE, and bias. Before that, anything I said
> would be a guess."

**2. "Why LoRa on the buoy? Why not 4G?"**
> "Three reasons. Power, cost, and coverage. LoRa uses far less electricity than a phone modem,
> and that matters on a small solar buoy. It is much cheaper. And out at sea, you cannot count
> on cellular. The 4G is still in the system, on shore, where there is power and signal."

**3. "Why not tsunami or typhoon warning?"**
> "That was never the plan. Those are different instruments, different physics, and decades of
> work behind them. We are not an official system. We make no such claim."

**4. "Where will it go?"**
> "Not chosen yet. And I will not name a place we have not spoken to. What we suggest is one
> town, one real problem, one trial site. Confirmed before we deploy, not after."

**5. "Why ₱90,000 to ₱150,000?"**
> "Because that is what things actually cost when they land here. Shipping, tax, and import
> charges add twenty to thirty percent. It also includes the shore radio, the small computer,
> and the SIM, which we originally did not know the price of. Plus calibration and spare parts.
> **These are planning numbers. Real quotes from three suppliers come before submission.**"

**6. "Can you really finish in four to five months?"**
> "Five months works if the scope stays locked, we buy in week one, and permits run alongside.
> Four months is our stretch goal. We are presenting it as a stretch goal, not a promise."

**7. "Is this your invention?"**
> "No. Our contribution is cheap integration, honest testing, and clear documentation. We used
> parts that already exist. Anyone can repeat our work. That is on purpose."

**8. "What if the radio drops?"**
> "The buoy keeps sensing and saves the readings with their original time stamps. When the
> signal returns it sends them in order and rejects duplicates. I showed you that live five
> minutes ago — you watched it break and recover."

## The three DOST questions — these decide it

**9. "Why should we fund you? What can you do that others cannot?"**
> "Because the thing already works. This is not a drawing.
>
> You could run all of this today, before you approve a single peso. The buoy software and its
> setup page. The data frame with its quality flags. The shore service with its simulator,
> database, API, and dashboard. The wave calculation. The GPS boundary check. And the radio
> buffering you watched break and recover.
>
> **Three students built that with no funding at all.**
>
> So what your money buys is not the ability to start. It buys three things we cannot get
> ourselves: the sensor hardware, the calibration reference, and a supervised sea trial.
>
> Those are what turn something that runs into something that is measured."

**10. "Can your team do this? How many of you are there?"**
> "**Four students**, and the work is already split.
>
> Jhon Ruzzel Correa — hardware, power, radio firmware.
> Gwyn Isabel Enriquez — the shore computer, the AI, the dashboard.
> Mayla Bacaltos and Gina Caballero — the thesis and the test records.
>
> Two advisers. Sir Jam on the papers, Sir Jeff on the hardware. And a third seat we are leaving
> open, for a software or AI mentor.
>
> We are also proposing this as an on-the-job training placement with DOST as host. Half OJT,
> half thesis. That way the work continues on a schedule instead of stopping at the end of the
> semester.
>
> **Where we are weak, stated plainly: none of us has done a sea deployment before.**
>
> That is exactly why the plan is staged. Bench first at Gate 02. Controlled testing at Gate 04.
> And that is why the mentor seat is part of our ask, not an optional extra."

**11. "Who owns the intellectual property? Who owns the data?"**
> "The intellectual property stays with us and with Fullbright College. This is thesis work.
>
> Where we are open is the data.
>
> We suggest **sharing ownership of the datasets** with the town we work with, or with DOST. And
> we built the archive to be opened from the start. Time stamped. Quality flagged. With the
> method and the limits written alongside it.
>
> I would put it this way. **A dataset only we can read is not worth collecting.** If the sea
> conditions are in a file a barangay cannot open, we have given them nothing.
>
> If a partner wants something different, we would rather agree it in writing now than assume it
> later."

---

# THE ASK

Say these five, in this order.

1. **Accept Project FALCON-01 as a DOST OJT placement** — half OJT, half thesis.
2. **A mentor seat** — one software or AI mentor, plus the third adviser.
3. **Help buying and building** — the ₱90,000 to ₱150,000 range.
4. **Calibration and site access** — a reference instrument and a supervised tank or pool test.
5. **Sea trial support and shared data ownership.**

---

# CHECKLIST

- [ ] `present.html?big=1` tested on the real projector
- [ ] Checked on a phone — panels open these on a phone during questions more often than you think
- [ ] Clicked `Interrupt LoRa` and `Inspect the Bay Station` once each
- [ ] **Said "simulated, not validated" out loud in chapters 05, 07, 08, and 10**
- [ ] Rehearsed questions 9, 10, and 11 out loud
- [ ] Timer ready for 20 minutes, with the cut list ready
- [ ] Finished on the ₱90,000 to ₱150,000 range and the five-point ask
- [ ] Date on the slide and the closing screen says **6 October 2026**
- [ ] Third mentor name updated in `story.js` if someone has been confirmed

---

## Three habits that keep you honest

The strength of this project is that it does not overclaim. Three habits protect that.

**1. No number leaves without a gate.** If anyone asks for an accuracy figure at any point, the
answer is the same every time: Gate 04, against a reference, with MAE, RMSE, and bias.

**2. Say the limit before they find it.** Chapters 05, 07, 08, and 10 each have a limit line
right after the impressive part. Say it first. It sounds like confidence, not weakness.

**3. "I don't know" is a full answer.** *"I don't know, and Gate 04 is where we find out"* is
a good answer to a DOST panel. Do not fill silence with a guess.