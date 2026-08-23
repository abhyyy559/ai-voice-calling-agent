# Project initial prompt-1

I am building an AI Voice Calling Agent as a serious project and I want you to act as a **senior voice-AI architect, telecom engineer, AI systems engineer and product strategist**.

Do not assume that the technologies or providers I mention are the best. I want an **independent second opinion** based on current information available on the internet. Research the current ecosystem where necessary and challenge weak assumptions.

## **PROJECT**

We are building a highly natural, real-time AI voice calling platform.

The initial version will focus **only on English**. Once the English voice experience reaches a very high level of quality, we will expand it to **Telugu**, and eventually support multiple Indian and international languages.

The goal is not simply to make an AI that can place a phone call.

The goal is to build a voice agent that feels as close to a natural human phone conversation as technically possible.

The agent should be able to:

* Make outbound phone calls.  
* Conduct natural conversations.  
* Listen continuously and understand the caller's response.  
* Handle interruptions naturally.  
* Stop speaking when the person interrupts.  
* Detect when the person has finished speaking.  
* Handle pauses, hesitation and incomplete sentences.  
* Maintain conversation context.  
* Respond quickly enough that the conversation does not feel robotic.  
* Collect structured information from the conversation.  
* Determine the outcome of the call.  
* Generate a transcript.  
* Generate a structured summary/result.  
* Track the status of every call.  
* Handle multiple calls concurrently.  
* Maintain an independent conversation state for every active call.

The system should eventually be **domain-independent** rather than being designed only for sales or lead qualification.

For example, one use case could be a college contacting absent students.

An administrator could upload a list of students containing information such as:

* Name  
* Phone number  
* Student ID  
* Other relevant information

The system would call the students individually and ask why they were absent.

After the campaign, the platform should provide results such as:

* Answered  
* Not answered  
* Busy  
* Failed  
* Reason for absence  
* Expected return/date  
* Other relevant information  
* Call duration  
* Transcript  
* AI-generated summary

The administrator should be able to export the final structured results, for example as an Excel/CSV file.

## **EXPECTED USER FLOW**

### **Administrator**

Website

↓

Upload CSV/Excel containing contacts

↓

Review contacts

↓

Start calling campaign

↓

System initiates calls

↓

AI conducts conversations

↓

Calls are independently tracked

↓

Transcripts and structured information are generated

↓

Administrator views campaign results

↓

Administrator exports results

Authentication and authorization are **not required during the initial development/prototype phase**. They will be added when moving toward production.

## **TELEPHONY REQUIREMENT**

The system needs to make real phone calls using a **proper Indian telephone number**.

We do not want the initial system to depend on an international number because the project will be demonstrated in India and calls should appear legitimate and trustworthy to recipients.

We need to understand the best current options for:

* Indian virtual numbers  
* Cloud telephony  
* Programmable voice  
* SIP  
* Voice APIs  
* Real-time bidirectional audio  
* Outbound calling  
* Call status tracking  
* Concurrent calls  
* Caller ID  
* Number provisioning  
* KYC requirements  
* DLT/regulatory requirements  
* Pricing  
* Number rental  
* Per-minute calling costs  
* Concurrency limits  
* API/WebSocket support  
* Academic/student access if available

Do not assume that a normal SIM/eSIM is the correct architecture. Evaluate **SIM/eSIM, virtual numbers, cloud telephony, SIP providers and other approaches** and explain which is actually appropriate for this project.

## **MOST IMPORTANT REQUIREMENT: VOICE QUALITY**

The primary differentiator of this project should be **conversation quality**, not merely the ability to make calls.

The agent should not feel like:

"User speaks → AI waits → AI thinks → AI speaks."

We want a natural conversation with:

* Very low perceived latency  
* Natural turn-taking  
* Natural pauses  
* Fast response generation  
* Reliable interruption handling  
* Barge-in support  
* Accurate speech recognition  
* Natural speech synthesis  
* Appropriate pacing  
* Natural sentence endings  
* Context awareness  
* Robust handling of hesitation  
* Robust handling of background noise  
* Ability to handle different accents  
* Ability to handle people speaking quickly or slowly  
* Ability to recover gracefully when speech recognition is uncertain

The final system should feel like an actual person is participating in the conversation rather than an obvious automated IVR system.

## **MULTILINGUAL ROADMAP**

Phase 1:

**English**

Phase 2:

**Telugu**

Phase 3:

**Telugu \+ English code-switching / Tanglish**

Phase 4:

**Multiple Indian languages**

Phase 5:

Other languages if technically and commercially justified.

Telugu is expected to be significantly more challenging because conversational Telugu requires good pronunciation, natural sentence rhythm, regional variation, code-switching, names, numbers and colloquial speech.

Do not assume that an English architecture will automatically produce high-quality Telugu.

We want to understand what must change between the English and Telugu versions.

## **RESEARCH QUESTIONS**

I want you to independently investigate the entire problem and answer the following.

### **1\. Telephony**

What are the best current options for building an AI voice calling system in India?

Compare the major relevant providers and approaches rather than giving only two options.

Compare:

* Indian virtual numbers  
* Cloud telephony providers  
* CPaaS providers  
* SIP providers  
* Programmable voice APIs  
* Real-time voice-AI-specific platforms  
* SIM/eSIM-based approaches

Explain the advantages, disadvantages, pricing model, Indian number availability, KYC, DLT requirements, API quality, WebSocket/audio streaming capabilities and concurrency.

### **2\. Real-time voice architecture**

What are the critical components required to make a genuinely high-quality real-time voice agent?

Explain the important concepts without assuming a specific vendor:

* Telephony  
* Audio streaming  
* STT  
* VAD  
* Endpoint detection  
* Turn-taking  
* Barge-in/interruption handling  
* Conversation orchestration  
* LLM  
* TTS  
* Audio buffering  
* Streaming  
* Latency management  
* Session management  
* Memory  
* Tool calling  
* Call state  
* WebSockets/SIP/RTP where relevant

Identify which components have the largest effect on perceived human quality.

### **3\. Latency**

What latency targets should we aim for?

Explain the complete latency pipeline from:

User stops speaking

→ speech detection

→ STT

→ reasoning

→ response generation

→ TTS

→ audio playback

Identify where latency normally occurs and how high-quality systems reduce perceived latency.

### **4\. Interruption and turn-taking**

This is one of the most important requirements.

Explain how high-quality voice agents handle:

* User interrupting the AI  
* AI stopping immediately  
* User pausing while thinking  
* User speaking in incomplete sentences  
* Simultaneous speech  
* Background speech  
* False interruption detection  
* Long pauses  
* Agent deciding when to respond

Explain what technologies and architectural patterns are normally used.

### **5\. Voice quality**

Research the current best approaches for achieving highly natural speech.

Compare current TTS approaches based on:

* Naturalness  
* Latency  
* Streaming  
* Emotional expression  
* Pronunciation  
* Conversational quality  
* English performance  
* Indian accent performance  
* Telugu capability  
* Cost

Do not assume open-source models are automatically better or cheaper.

### **6\. STT quality**

Compare the best current speech recognition approaches for conversational phone audio.

Consider:

* English  
* Indian accents  
* Telephone audio  
* Background noise  
* Streaming  
* Latency  
* Accuracy  
* Telugu  
* Code-switching

### **7\. LLM strategy**

Determine whether a voice agent actually needs a large reasoning model.

Compare:

* Small/fast models  
* Large models  
* Local models  
* Cloud models  
* Hybrid architectures  
* Multiple-model architectures

Explain where intelligence is actually required and where deterministic logic is preferable.

### **8\. Cost**

Estimate the realistic cost per minute of operating the system.

Break down:

* Indian telephone number  
* Telephony  
* STT  
* LLM  
* TTS  
* Infrastructure  
* Storage  
* Recording  
* Transcription  
* Other relevant costs

Give approximate costs for:

* 100 calls/month  
* 1,000 calls/month  
* 10,000 calls/month  
* 100,000 calls/month

Also compare the cost with traditional human calling.

### **9\. Scalability**

Explain how the system should handle:

* 1 concurrent call  
* 10 concurrent calls  
* 100 concurrent calls  
* 1,000 concurrent calls

Identify the technical bottlenecks and provider limitations.

### **10\. Indian telecom/legal considerations**

Research the current Indian requirements for AI-generated outbound phone calls.

Specifically investigate:

* KYC  
* DLT  
* Caller ID  
* Consent  
* Promotional vs transactional calls  
* Recording  
* Privacy  
* Data protection  
* Automated calling restrictions  
* Number provisioning  
* Institutional/college use cases

Do not make legal assumptions. Use current authoritative sources wherever possible.

### **11\. English → Telugu transition**

Explain what will need to change when moving from English to Telugu.

Investigate:

* Telugu STT  
* Telugu TTS  
* Telugu pronunciation  
* Regional dialects  
* Code-switching  
* Tanglish  
* Names  
* Numbers  
* Locations  
* Colloquial speech  
* Conversational Telugu

Identify the biggest technical gaps in the current ecosystem.

### **12\. Competitive landscape**

Research current companies/products that are doing high-quality AI phone conversations.

Do not only list them.

Analyze what appears to differentiate the strongest systems in:

* Latency  
* Voice quality  
* Interruption handling  
* Turn-taking  
* Indian languages  
* Telugu  
* Telephony infrastructure  
* Cost  
* Developer flexibility

Do not assume that a company's marketing claims represent its actual technical advantage.

### **13\. Critical risks**

Identify the biggest reasons this project could fail.

I specifically want you to challenge the project on:

* Robotic voice  
* High latency  
* Poor interruption handling  
* Bad turn detection  
* Hallucinations  
* Incorrect information extraction  
* Telephone audio degradation  
* Poor Indian accent recognition  
* Telugu quality  
* High per-minute costs  
* Telecom restrictions  
* Provider lock-in  
* Concurrency limitations  
* Unreliable call connections  
* Poor scalability  
* Privacy/security issues

### **14\. Recommended technology strategy**

Only AFTER independently researching all of the above, recommend:

1. Best telephony provider(s)  
2. Best Indian number approach  
3. Best STT approach  
4. Best TTS approach  
5. Best LLM strategy  
6. Best real-time communication architecture  
7. Best backend architecture  
8. Best database  
9. Best deployment approach  
10. Best development roadmap

Give multiple alternatives where appropriate.

Do not recommend a technology merely because it is popular.

## **IMPORTANT**

I am not asking you to immediately build the system.

I am currently trying to understand the **complete technical and commercial landscape** before development begins.

I want a research-grade answer based on current information.

Use current web sources wherever possible, especially official provider documentation and pricing pages.

Clearly distinguish between:

* Verified facts  
* Provider claims  
* Your technical inference  
* Your recommendation

Most importantly, **challenge my assumptions instead of agreeing with them**.

The final objective is to build an English voice calling agent whose conversation quality is significantly better than a typical basic AI calling implementation, and then use the lessons from the English system to build a highly natural Telugu and eventually multilingual voice agent.

# GLM 5.2 approch

1\. Telephony: The Indian Landscape  
Challenging Assumption: Do not assume that a normal SIM/eSIM is the correct architecture.  
Verdict: A SIM/eSIM (even via gateways like Truphone or Twilio Mobile) is entirely the wrong approach for automated outbound calling in India. It lacks scalability, programmatic control, and violates TRAI's commercial usage guidelines for automated bulk calling.

Verified Facts & Provider Comparison (India):

Twilio (Global CPaaS):  
Pros: Best developer experience, excellent WebSocket/Media Streams API for real-time bidirectional audio.  
Cons: Indian numbers are difficult to provision (requires heavy KYC). Often routes calls via US/UK servers, introducing 150-300ms network latency before audio processing even begins.  
Pricing: \~$0.013/min outbound to India. Number rental \~$1.15/mo.  
Exotel / Kaleyra / Ozonetel (Indian CPaaS):  
Pros: Deeply integrated with Indian telecom (Jio, Airtel, Vi). Excellent DLT compliance dashboards. Local data centers \= low network latency.  
Cons: Their core APIs are built for legacy IVR, not real-time AI. Many do not offer true bidirectional WebSocket streaming; they use POST APIs to trigger pre-recorded audio or basic dynamic TTS.  
Pricing: \~₹0.80 \- ₹1.50/min. Number rental \~₹200-₹300/mo.  
Plivo / Sinch:  
Pros: Sinch (via Voice API) and Plivo offer decent SIP trunking and WebSocket support. Plivo has good Indian coverage.  
Cons: Still require strict DLT registration.  
Voice-AI Specific Platforms (Vapi, Retell AI, Bland AI):  
Pros: Out-of-the-box orchestration of STT, LLM, TTS, and telephony. You can bring your own Twilio/Plivo numbers.  
Cons: High markup on usage (\~$0.10 \- $0.15/min). May not fully support Indian DLT routing natively.  
Recommendation for Telephony: Do not build your own SIP/PBX infrastructure initially. Use Twilio Media Streams (bringing your own Indian virtual number via a local CPaaS provider that supports SIP forwarding, or using Twilio's Indian mobile numbers if you qualify). Alternatively, Exotel recently launched real-time WebSocket APIs—verify their latency. If you want ultimate control, rent an Indian SIP trunk from a local provider and bridge it to your application using FreeSWITCH or Asterisk.

2\. Real-time Voice Architecture  
To achieve "human-like" quality, you cannot use a sequential pipeline (Record \-\> STT \-\> LLM \-\> TTS \-\> Play). You must use a Streaming Event-Driven Architecture.

Critical Components:

Telephony Bridge: Connects PSTN to your server via WebSocket (RTP/Opus audio).  
Audio Streaming: Must use 16kHz, 16-bit linear PCM. Phone lines are narrowband (8kHz mu-law), but upsampling to 16kHz gives STT models better accuracy.  
VAD (Voice Activity Detection): WebRTC VAD or Silero VAD. Runs locally on the audio stream to detect speech presence.  
Endpoint Detection: The hardest part. Determines when the user finished speaking. Relies on VAD silence thresholds \+ LLM intent parsing.  
Turn-taking / Barge-in Orchestrator: A central state machine that tracks who is "holding the floor." If the AI is speaking and VAD detects user audio, it sends a "kill signal" to the TTS audio buffer.  
Streaming STT: Continuously transcribes audio chunks.  
LLM: Generates tokens in a stream.  
Streaming TTS: Converts incoming LLM tokens to audio chunks before the LLM finishes generating the full sentence.  
Largest Effect on Perceived Quality: VAD/Endpoint detection and Barge-in orchestration. A highly intelligent LLM with poor endpoint detection feels like a walkie-talkie conversation.

3\. Latency  
Human conversational latency (the gap between one person finishing and the other starting) is typically 200-400ms. Anything over 800ms feels like a delay.

Pipeline Breakdown & Targets:

Network Audio Transport (Telephony → Server): 40-80ms (Use AWS Mumbai ap-south-1 or local Indian DC).  
VAD & Endpointing: 100-300ms (Requires waiting for silence to ensure the user actually stopped).  
STT Processing: 100-200ms (Streaming STT returns text as soon as audio stops).  
LLM Time-to-First-Token (TTFT): 150-300ms (Crucial. Must use fast inference providers).  
TTS Time-to-First-Audio (TTFA): 100-200ms.  
Audio Transport back to PSTN: 40-80ms.  
Total Target: \~550ms \- 1.1s.  
How to reduce perceived latency further:

Speculative Execution: While the user is speaking, run an intent classifier on the partial transcripts. If the user is clearly saying "Yes", pre-generate the next logical response before the user even finishes.  
Chunked TTS: Send TTS requests sentence-by-sentence, or even clause-by-clause.  
Backchanneling: If endpointing takes longer than 1s, inject a quick "Hmm", "Right", or "I see" to fill the dead air.  
4\. Interruption and Turn-taking  
Challenging Assumption: The system should stop speaking when the person interrupts.  
Architectural reality: If you simply cut the audio upon hearing any voice, background noise, TV sounds, or the caller's own echo will constantly interrupt the AI, ruining the experience.

How High-Quality Systems Handle This:

Echo Cancellation: Hard on PSTN, but necessary.  
Energy Thresholds \+ VAD: Background noise has different acoustic signatures than directed speech.  
Semantic Barge-in: Instead of just VAD, use a fast STT model to transcribe the interrupting audio. If it detects words (not just noise), send the kill signal to the TTS buffer.  
Handling Pauses/Hesitation: If the user pauses, STT yields a partial transcript. The LLM classifies: "Is this a complete thought?" If no, the orchestrator waits. If the pause exceeds 2 seconds, the AI can use a "floor-holding" phrase: "Take your time."  
5\. Voice Quality (TTS)  
Challenging Assumption: Open-source models are automatically better or cheaper.  
Verdict: False. Open-source models (like Bark, VITS, XTTS) require heavy GPU provisioning. At 100 concurrent calls, the cost of hosting real-time TTS GPUs often exceeds API costs, and latency is generally worse.

Current Best Approaches:

ElevenLabs: Best naturalness and emotion. Conversational latency is \~400ms. English is unmatched. Has Telugu support, but pronunciation of complex Telugu words/names can be Anglicized. Cost: \~$0.30/1000 chars.  
Cartesia (Sonic): Insanely fast (TTFA \< 100ms). Excellent for conversational English. Highly recommended for low-latency barge-in. Cost: \~$0.10/1000 chars.  
PlayHT (Play3): Low latency, good cloning, decent Indian accents.  
Google Cloud TTS / Azure TTS: Extremely reliable, excellent Telugu voices (specifically trained on native speakers). But sounds more "robotic" than ElevenLabs in conversational English.  
6\. STT Quality  
For phone audio (8kHz), you must use models trained on telephone datasets.

Deepgram (Nova-2): The industry standard for speed and accuracy. Excellent on noisy audio. Strong Indian English accents. Latency \< 150ms. Cost: \~$0.0043/min.  
AssemblyAI: Highly accurate, great semantic features (sentiment, speaker diarization), but slightly higher latency than Deepgram.  
Google Speech-to-Text: Best for Telugu. Their multilingual models handle code-switching (Tanglish) natively better than Deepgram currently does.  
OpenAI Whisper (API): Too slow for real-time barge-in. High hallucination rate on silence/noise.  
7\. LLM Strategy  
Challenging Assumption: A voice agent actually needs a large reasoning model.  
Verdict: False. GPT-4o, Claude 3.5 Sonnet, or o1 are overkill for a phone call. Their high TTFT (Time to First Token) ruins the conversation, and their reasoning capabilities lead to over-explaining.

The Strategy:

Core Dialogue Model: Use a fast, highly capable model. Llama 3.1 8B (via Groq or self-hosted), GPT-4o-mini, or Claude 3 Haiku. These have TTFT of \< 200ms.  
Tool Calling / Function Calling: Use the LLM only to extract structured data and determine conversation state (e.g., absence\_reason\_captured: true).  
Deterministic Logic: For things like "Please spell your student ID," use deterministic string matching, not LLM parsing.  
Hybrid Architecture: Use a fast classifier model to determine intent, and route the conversation. Only escalate to a heavier model if complex reasoning is strictly required (rare in outbound transactional calls).  
8\. Cost Analysis  
Per-Minute Breakdown (English):

Telephony (India): ₹1.00 ($0.012)  
STT (Deepgram): ₹0.35 ($0.004)  
LLM (GPT-4o-mini / Llama 8B): ₹0.30 ($0.004)  
TTS (ElevenLabs/Cartesia): ₹0.50 ($0.006)  
Infrastructure/WebSockets: ₹0.20 ($0.002)  
Total per minute: \~₹2.35 ($0.028)  
Monthly Estimates (Assuming 3-min avg call duration):

100 calls/month (300 mins): \~₹705  
1,000 calls/month (3,000 mins): \~₹7,050  
10,000 calls/month (30,000 mins): \~₹70,500  
100,000 calls/month (300,000 mins): \~₹590,000 (volume discounts apply)  
Comparison to Human: A human BPO worker in India costs \~₹15,000 \- ₹25,000/month plus overhead. A human can make \~50-80 calls a day. AI can make 10,000s a day. The ROI of AI is massive at scale.

9\. Scalability  
1 Concurrent Call: Can run on a single mid-tier VM.  
10 Concurrent Calls: Needs a dedicated WebSocket server \+ external API integrations.  
100 Concurrent Calls: Requires load-balanced WebSocket nodes. Deepgram/ElevenLabs handle concurrency easily. LLM API concurrency limits become the bottleneck here.  
1,000 Concurrent Calls: Requires a microservices architecture. State management (Redis) is critical. SIP trunking concurrency limits (telephony provider) will require enterprise tier negotiations.  
Bottlenecks: LLM rate limits (tokens per minute) and TTS concurrency limits.

10\. Indian Telecom/Legal Considerations  
Verified Facts (TRAI Regulations):

DLT (Distributed Ledger Technology): Mandatory in India. You must register your business, get a Header ID (Sender ID), and register the content template of your calls. Critical: AI conversational scripts are hard to template because the exact words change. You must register a generalized transactional template.  
Promotional vs. Transactional: You cannot use promotional routes for automated calls without strict consent mechanisms. College absence calling is arguably transactional (service/relationship based), which allows calling any time between 10 AM and 9 PM.  
AI Disclosure: While specific AI calling laws are evolving, TRAI mandates that automated calls must not mislead. Using a human-sounding AI without disclosing it's an assistant is a legal gray area that is currently being scrutinized. Proceed with caution.  
Caller ID: Must display the registered Indian virtual number.  
11\. English → Telugu Transition  
Challenging Assumption: An English architecture will automatically produce high-quality Telugu.  
Verdict: Completely false. Moving to Telugu breaks standard STT/TTS pipelines.

What must change:

Code-Switching (Tanglish): Users will say "Nenu illa unnanu, fever vastundi." (I am at home, getting a fever). Deepgram struggles with this natively. You must use Google Speech-to-Text with automatic language detection or multilingual models.  
TTS: ElevenLabs Telugu often sounds like a foreigner reading Telugu phonetically. You must evaluate Azure Neural TTS (which has specifically trained Telugu voices like Shruti) or Bhashini (Indian government initiative) for natural Telugu.  
Pronunciation: Telugu names (e.g., "D. Venkateshwarlu") and places will be butchered by standard TTS. You need custom pronunciation dictionaries (lexicons).  
Grammar/Syntax: Telugu is Subject-Object-Verb. The LLM might generate English syntax translated to Telugu, which sounds robotic. The system prompt must enforce native Telugu syntax.  
12\. Competitive Landscape  
Current Leaders:

Vapi.ai: Excellent orchestration. Fast, handles barge-in well. Highly developer-focused.  
Skit.ai (Indian Company): Very strong in Indian context, debt collection, and multilingual support. They use custom acoustic models rather than just off-the-shelf APIs, giving them an edge in noisy Indian phone networks.  
Retell AI: Great turn-taking models. They invested heavily in custom endpointing algorithms.  
Gnani.ai (Indian): Strong local STT/TTS models built for Indian languages.  
Differentiators: The strongest systems do not rely on standard OpenAI/Deepgram integrations. They build custom endpointing models trained on conversational data, and they use semantic barge-in rather than acoustic barge-in.

13\. Critical Risks (Challenging the Project)  
Bad Turn Detection: The project assumes the system can tell when a person finishes speaking. Over Indian mobile networks with high background noise, VAD will either cut users off constantly or hang in dead silence. Mitigation: Build a custom dual-model endpointer (VAD \+ fast LLM to validate if the sentence is complete).  
Telephony Lock-in: If you build directly on Exotel's specific API, you cannot scale globally or switch providers if quality drops. Mitigation: Abstract the telephony layer. Use SIP/WebRTC bridges.  
LLM Hallucination on Data Extraction: If the AI calls a student, and the student says "I will come on Monday," the LLM might extract "Next Monday" or hallucinate a date. Mitigation: Use strict JSON schemas and Tool Calling (Function Calling). Do not rely on free-text summarization for the final exported CSV.  
DLT Blocking: TRAI is aggressive. If recipients mark your AI calls as spam, your virtual number will be blocked within days. Mitigation: Ensure the AI clearly states the purpose of the call within the first 3 seconds.  
14\. Recommended Technology Strategy  
Based on the independent research above, here is the optimal path forward:

1\. Telephony Provider:

Prototype: Twilio (for rapid WebSocket Media Streams dev) OR Exotel (if Indian number DLT is the immediate priority).  
Scale: Rent an Indian SIP trunk from a local provider (e.g., Jio/Airtel enterprise) and bridge via FreeSWITCH.  
2\. STT:

English: Deepgram (Nova-2 conversational model). Unbeatable speed.  
Telugu/Tanglish: Google Speech-to-Text (V1 API with auto\_decoding and multilingual config).  
3\. TTS:

English: Cartesia Sonic (for lowest latency) or ElevenLabs (for best naturalness).  
Telugu: Microsoft Azure Neural TTS (Telugu voices are far superior to ElevenLabs for native pronunciation).  
4\. LLM:

Llama 3.1 8B (served via Groq for ultra-fast TTFT) or GPT-4o-mini. Keep prompts incredibly short. Use JSON tool calling for data extraction.  
5\. Real-time Architecture:

Do not build polling loops. Use an event-driven WebSocket orchestrator. As audio streams in, push it to STT. As STT yields text, push to a state machine. If state \== "user\_turn\_complete", stream prompt to LLM. Stream LLM tokens to TTS. Stream TTS chunks back to the WebSocket.  
Implement a "barge-in" event bus: if VAD triggers during "ai\_speaking" state, send a kill signal to the TTS stream.  
6\. Backend Architecture:

Node.js or Go for the real-time WebSocket layer (critical for I/O concurrency).  
Python/FastAPI for the LLM/STT integration and business logic.  
Redis for ephemeral call state (who is speaking, current prompt context).  
Celery/RabbitMQ for background tasks (transcription, summary generation, CSV export).  
7\. Database:

PostgreSQL for relational data (Campaigns, Contacts, Call Logs, Results).  
8\. Deployment:

AWS Mumbai (ap-south-1). This is non-negotiable for latency. Hosting in US/EU will add 250ms+ of network latency, ruining the human feel.  
9\. Development Roadmap:

Phase 1 (Weeks 1-3): Text-to-Speech conversational loop in terminal. Master the VAD, STT, and TTS pipeline before touching telephony. Aim for \<800ms latency.  
Phase 2 (Weeks 4-6): Integrate Twilio/Exotel WebSocket. Handle real PSTN audio (mu-law to PCM conversion). Implement barge-in.  
Phase 3 (Weeks 7-8): Implement the LLM state machine, tool calling for student data extraction, and campaign management DB.  
Phase 4: Begin Telugu evaluation. Swap Deepgram for Google STT, ElevenLabs for Azure. Evaluate code-switching failure rates.

# k3 approch

# 1\. Telephony: Best Current Options for AI Voice Calling in India

## The Core Architectural Decision: SIM/eSIM vs. Cloud Telephony vs. SIP

Your assumption that a "proper Indian telephone number" requires evaluating SIM/eSIM is worth challenging. For a scalable AI voice platform, a physical SIM or eSIM is almost never the correct architecture. Here is why:  
Table

| Approach | What It Is | Pros | Cons | Verdict |
| :---- | :---- | :---- | :---- | :---- |
| Physical SIM / eSIM | Consumer mobile SIM in a GSM gateway or Android device | Very low per-minute cost; no KYC beyond normal SIM | Illegal/gray-area for commercial bulk calling; no API control; no concurrent calls; TRAI considers this "gray traffic"; no call recording consent automation; device failure \= downtime; no CLI management | Inappropriate |
| Cloud Telephony (CPaaS) | Exotel, Ozonetel, Knowlarity, Plivo, Twilio | Full API control; WebSocket/RTP streaming; DLT compliance support; concurrent scaling; legitimate CLI | Higher per-minute cost; KYC required; monthly commitments | Correct for prototypes and mid-scale |
| Direct SIP Trunk | Direct carrier relationship with Airtel Business, Jio Business, Tata | Lowest per-minute cost at scale; best latency; full control | You become your own CPaaS; need SBC config, codec negotiation, DLT plumbing, telecom engineer | Correct at 20L+ minutes/month |
| Hybrid | Direct SIP for volume \+ CPaaS for overflow/failover | Cost optimization \+ operational safety | Complexity | Correct for mature scale |

Verified fact: Direct SIP trunking with Airtel/Jio/Tata at 20 lakh+ minutes/month drops outbound rates to ₹0.60–₹1.20/min versus ₹0.80–₹1.80 through aggregators.  
Technical inference: For your prototype and early production (under \~10,000 calls/month), a CPaaS provider is the only rational choice. A SIM-based approach would require you to build hardware redundancy, call rotation to avoid carrier spam flags, and manual DND scrubbing — all of which a CPaaS handles.

## Provider Comparison for India (2026)

Table

| Provider | India Focus | Outbound ₹/min | DID Provisioning | DLT Support | WebSocket/RTP Streaming | Best For |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Exotel | Very high | ₹0.80–1.00 | 2–5 days | Strongest operational support | AgentStream (\<50ms) | India-native voice AI; DLT hand-holding |
| Ozonetel | Very high | Competitive | 3–7 days | Strong | Yes | Contact-center workflows; unlimited minute plans |
| Knowlarity | High | Competitive | 2–5 days | Strong | Yes | Mid-market with compliance needs |
| Plivo | Moderate | ₹0.80–1.20 | 24–48 hours | Competent | Yes | Developer-led; global expansion later |
| Twilio | Low in India | ₹1.20–1.50 | 24–48 hours | Thinnest | Yes | Global-first teams; weak India-specific compliance |
| Direct SIP (Airtel/Jio) | N/A | ₹0.60–1.20 | Weeks | You handle it | Raw SIP/RTP | 20L+ minutes/month with telecom engineer |

Verified fact: Exotel's pricing is typically ₹0.80–1.00 for outbound and ₹0.30–0.50 for inbound, with AgentStream providing \<50ms media latency for AI streaming.  
Verified fact: Plivo and Twilio provision new Indian DIDs in 24–48 hours versus 2–7 business days for India-native providers.  
Challenge to your assumption: Twilio is not the best choice for India despite its global popularity. Its India DLT support is the thinnest among major providers, and its India outbound rates are 20–50% higher than Exotel/Plivo. If you start with Twilio because "it's what everyone uses," you will pay a premium and struggle with TRAI compliance.

## KYC, DLT, and Regulatory Requirements

DLT Registration (for SMS): If your system sends any SMS (appointment reminders, OTPs, consent confirmations), you must register on a TRAI-approved DLT platform. This is a three-phase process: Entity Registration → Sender ID Registration → Template Registration. Cost: ₹5,000 \+ GST for entity registration; ₹50,000 \+ GST for telemarketer delivery function.  
For voice calls specifically: The DLT framework is primarily SMS-oriented, but TRAI's TCCCPR regulations and the new Digital Consent Registry apply to voice communications as well. You must:

* Register as a telemarketer if making outbound commercial calls  
* Scrub against DND (Do Not Disturb) lists  
* Maintain call logs for 1 year  
* Implement recording disclosure  
* Restrict calling hours (typically 9 AM – 9 PM for marketing; 9 AM – 7 PM for BFSI)

Critical 2026 update: TRAI has introduced mandatory AI disclosure for AI-generated voice calls. Your agent must clearly state at the beginning of the call that it is AI-powered, the purpose, company identification, and how to opt out. Penalties for non-compliance reach up to ₹10 lakh, with repeat offenders facing disconnection and blacklisting.  
Number series restrictions:

* 140 series: Strictly for marketing/promotional calls  
* 160 series: Reserved for transactional/service calls from regulated entities (RBI, SEBI, IRDAI, PFRDA)  
* Cross-selling during service calls on 160 series is prohibited

For your college absentee use case: This is arguably a transactional/service call (educational institution contacting enrolled students about attendance). You may qualify for 160-series numbers or standard DIDs, but you still need explicit consent or a legitimate educational relationship. Do not assume "we're a college" exempts you from consent requirements.  
---

# 2\. Real-Time Voice Architecture

The architecture is a cascaded pipeline with intelligent orchestration, not a single model. Here are the critical components and their quality impact:

## Component Breakdown

Table

| Component | Function | Quality Impact | Typical Latency |
| :---- | :---- | :---- | :---- |
| Telephony | PSTN/SIP connectivity, audio capture | Medium — 8kHz μ-law degrades audio | 20–100ms network |
| VAD (Voice Activity Detection) | Detects if human is speaking | Critical — bad VAD \= false interruptions or delayed responses | Runs continuously |
| STT (Speech-to-Text) | Converts speech to text | Critical — errors cascade to LLM | 50–300ms (streaming) |
| Endpoint Detection | Decides when user has finished speaking | Critical — hardest problem in voice AI | 100–400ms |
| LLM | Reasoning, response generation | High — but latency matters more than size | 100–500ms TTFT |
| TTS (Text-to-Speech) | Converts response to audio | Critical — dominant cost and perceived quality | 40–200ms TTFB |
| Turn-Taking Orchestrator | Coordinates who speaks when | Critical — defines "naturalness" | Orchestration layer |
| Barge-In Handler | Stops AI when user interrupts | Critical — worst failure mode is talking over user | \<100ms stop time |
| Session Manager | Maintains call state, context, memory | High — prevents repetition, maintains flow | N/A |
| Tool Calling | Extracts structured data, triggers actions | Medium — latency spikes if synchronous | 100–500ms |

## The Streaming Principle

The single most important architectural concept: Every stage must stream into the next without waiting for completion.

* STT emits partial transcripts every \~50ms  
* LLM streams tokens as they generate  
* TTS streams audio chunks before the full response exists  
* Endpoint detection uses a small neural model updating probability dozens of times per second

Technical inference: A non-streaming architecture adds 2–4 seconds of perceived latency. A streaming architecture can achieve \~600ms end-to-end.

## What Actually Differentiates Production-Grade Systems

In 2026, the raw STT/LLM/TTS components are commoditized. What separates "demo" from "production-grade" is:

1. Endpoint detection quality — A naive timeout (e.g., 1.5s silence) destroys naturalness. Humans pause mid-sentence, say "um," and breathe. The 2026 answer is a trained conversational endpoint model.  
2. Barge-in recovery — When interrupted, the system must stop TTS within 100ms, discard the remaining planned response, and start a fresh STT stream without losing context.  
3. VAD tuning — Semantic VAD (understanding meaningful speech vs. background noise) outperforms energy-based VAD.  
4. Turn-taking model — A dedicated small model that decides when the human has finished, considering prosody, semantics, and conversational history.

---

# 3\. Latency Targets

## The Complete Latency Pipeline

Table

| Stage | Target | Where Latency Hides | Optimization |
| :---- | :---- | :---- | :---- |
| Network round-trip | 20–80ms | Physical distance to server | Edge deployment (Mumbai/Bangalore) |
| VAD detection | 10–50ms | Energy vs. semantic detection | Use semantic VAD (neural) |
| Endpoint detection | 100–300ms | Conservative timeouts | Train/fine-tune endpoint model on conversational data |
| STT | 50–200ms | Waiting for complete utterance | Streaming STT with partial transcripts |
| LLM TTFT | 100–400ms | Large model inference time | Use small/fast model; streaming; speculative decoding |
| TTS TTFB | 40–200ms | First audio chunk generation | Streaming TTS; optimize for speed |
| Audio playback | 20–50ms | Buffering | Minimal buffering; WebRTC if possible |
| TOTAL | \<700ms |  |  |

Verified fact: Under \~700ms end-to-end response time is the threshold where conversation feels human. Above that, callers interrupt, repeat themselves, and hang up.  
Where latency actually occurs: Most latency hides in turn-taking decisions and LLM time-to-first-token, not STT or TTS. A typical budget: network 50ms, VAD/turn-taking 200ms, LLM TTFT 250ms, TTS first audio 100ms. STT runs largely in parallel with speech.

## How High-Quality Systems Reduce Perceived Latency

1. Predictive TTS: Start generating audio for high-probability responses before the LLM finishes.  
2. Filler audio: Inject "um," "hmm," or "let me check" while tools run.  
3. Progressive responses: Speak the first clause while generating the rest.  
4. Edge deployment: Run VAD/STT/endpoint models in Mumbai/Bangalore, not US-East.  
5. Speculative execution: Pre-generate likely follow-up responses.

---

# 4\. Interruption and Turn-Taking

This is the most technically difficult requirement and the primary differentiator between robotic and natural systems.

## Handling Specific Scenarios

Table

| Scenario | Technique | Common Failure |
| :---- | :---- | :---- |
| User interrupts AI | Barge-in detection → immediate TTS stop → flush buffer → new STT stream | TTS continues for 500ms+; stale response plays |
| AI stopping immediately | \<100ms TTS cancellation; discard unplayed audio chunks | Partial word cutoff sounds robotic |
| User pausing while thinking | Semantic endpoint model distinguishes "thinking pause" from "finished" | Naive timeout cuts off user or delays response |
| Incomplete sentences | LLM trained on conversational repair; ask clarifying questions | AI treats incomplete input as complete |
| Simultaneous speech | Crosstalk detection; defer to user; mark overlapping audio | Both speakers continue; chaos |
| Background speech | Directional/noise-robust VAD; spectral subtraction | False trigger from TV/radio |
| False interruption detection | Hysteresis in barge-in threshold; confirm with 200ms lookahead | AI stops for every cough |
| Long pauses | Progressive "are you there?" prompts; comfort noise | Dead silence feels abandoned |
| Agent decides when to respond | Turn-taking probability model combining acoustic \+ lexical \+ conversational features | Always responds too fast or too slow |

## Architectural Patterns

The 2026 standard pattern: A small neural turn-taking model (often \~100M parameters) runs on the audio stream, outputting a probability of "user has finished" dozens of times per second. This model is trained on real conversational telephone audio.  
Barge-in implementation: The system maintains two audio streams:

1. Agent output stream (TTS → telephony)  
2. User input stream (telephony → VAD → STT)

When VAD detects user speech during agent output, a barge-in event fires. The orchestrator must:

1. Send TTS stop signal (\<50ms)  
2. Flush remaining TTS buffer  
3. Reset STT stream (or maintain separate context)  
4. Start new inference turn

Technical inference: Poor barge-in handling is the \#1 reason users perceive voice AI as "robotic." A system that talks over the user for even 300ms feels fundamentally broken.  
---

# 5\. Voice Quality (TTS)

## Current TTS Comparison (2026)

Table

| Provider | Model | Naturalness | Latency (TTFB) | Streaming | Indian Accent | Telugu | Cost/1M chars | Best For |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| ElevenLabs | v3 / Flash v2.5 | Excellent (\#4 ELO) | \~100ms | Yes | Good (English) | Limited | \~$100 | Premium English; voice cloning |
| Cartesia | Sonic-3 / Sonic-3.5 | Very good | \~40–90ms | Yes | Moderate | No | \~$39 | Ultra-low latency |
| Inworld | TTS-2 / TTS 1.5 Max | Excellent (\#1–2 ELO) | \~120–155ms | Yes | Good | No | \~$12.50–35 | Expressive realtime; steerable |
| Google | Gemini 3.1 Flash TTS | Excellent (\#2 ELO) | Variable | Yes | Good | Good | \~$36.60 | Multilingual; Indian languages |
| Deepgram | Aura-2 | Good | \~313ms | Yes | Moderate | No | \~$13.50 | Integrated stack; cost |
| VoisLabs | Default | Good (Indian languages) | Moderate | Batch+Stream | Good | Native-quality | \~₹8.3/min | Indian languages primary |
| DesiVocal | Default | Moderate | Moderate | Yes | Good | Yes | \~₹399/mo | Indian-built; INR billing |
| OpenAI | gpt-4o-mini-tts | Good | Moderate | Yes | Moderate | No | Bundled | OpenAI ecosystem |

Verified fact: Inworld TTS 1.5 Max ranks \#1 on Artificial Analysis Speech Arena ELO (1,208), followed by Google Gemini 3.1 Flash TTS (1,206), with ElevenLabs v3 at \#4 (1,178).  
Verified fact: For Indian languages specifically, VoisLabs and Narakeet lead. VoisLabs offers native Telugu voices, English→Telugu transliteration, and code-mixed ("Tanglish") handling. ElevenLabs and Murf are over-indexed for this market at their current price points.

## Challenge to Your Assumption

Do not assume open-source TTS is better or cheaper. Open-source models like Coqui TTS, Piper, or XTTS require significant GPU infrastructure, voice cloning data, and tuning to sound natural. For a small team, the engineering cost exceeds API costs. Commercial APIs also update models continuously — a hidden operational cost of self-hosting.  
For English: ElevenLabs, Inworld, and Google Gemini Flash TTS are the top tier. Cartesia wins on raw latency but sacrifices some expressiveness.  
For Telugu: This is where the ecosystem gaps appear. ElevenLabs has Telugu voices but quality is described as "limited" for conversational use. VoisLabs and DesiVocal are specifically built for Indian languages. Google Cloud TTS has Telugu support but conversational naturalness is questionable. The biggest gap: No major realtime TTS provider offers truly natural, conversational Telugu with emotional range and code-switching.  
---

# 6\. STT Quality

## Comparison for Conversational Phone Audio

Table

| Provider | Model | English WER | Phone Audio WER | Indian Accent | Telugu | Streaming Latency | Cost/min | Best For |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Deepgram | Nova-3 | \~5.26% (batch) | 21.8% (CallHome) | Good | Poor | \<300ms | $0.0043 | Real-time voice agents; speed |
| Deepgram | Flux | N/A | 15.58% (realtime) | Good | Poor | \<300ms | $0.0065 | Conversational agents |
| AssemblyAI | Universal-3.5 Pro | \~7.0% (aggregate) | \~23.4% | Good | No | \~300ms | $0.0035 | Max accuracy; post-processing |
| Whisper (OpenAI) | Large-v3 | \~8–12% real-world | \~26.4% | Good | \~21–28% | 1–5s (batch) | Free (self-host) / $0.006 | Multilingual; Indian languages |
| Google | Chirp 2 | \~3–4% clean | \~7–10% noisy | Very good | Good | \~350ms | $0.006 | Indian languages |
| ElevenLabs | Scribe v2 | Good | Good | Good | Unknown | Realtime | $0.0065 | Integrated with ElevenLabs TTS |

Verified fact: On conversational phone audio (CallHome benchmark), Deepgram Nova-3 achieves 21.8% WER versus Whisper's 26.4% and AssemblyAI's 23.4%. Even the best engine misses roughly 1 word in 5 on phone audio.  
Verified fact: Whisper Large-v3 achieves \~21.5% WER on Hindi FLEURS benchmark. Telugu WER on Whisper (from academic research) is approximately 20.3–26.7% depending on model size and prompting.  
Critical finding for Indian accents: The Voice of India benchmark found that best-performing models scored 5–6% WER on Indo-Aryan languages (Hindi, Bengali) but 15–20% on Dravidian languages (Tamil, Telugu, Malayalam).  
Challenge to your assumption: Deepgram is the dominant choice for English voice agents due to speed and cost, but its multilingual accuracy is significantly worse than alternatives. For Telugu, Google Cloud STT and Whisper are better starting points, though all options have substantial quality gaps for conversational Telugu.

## Code-Switching (Tanglish)

This is a major unsolved problem. When speakers switch between Telugu and English mid-sentence:

* Deepgram Nova-3 Multilingual achieves 12.22% WER on code-switching audio  
* AssemblyAI Universal-3.5 Pro achieves 7.69% WER on code-switching  
* Whisper handles Hinglish/Tanglish better than most commercial APIs due to its diverse training data, but still struggles with mid-sentence switches

Technical inference: For Phase 3 (Telugu \+ English code-switching), you will likely need a custom solution or significant prompt engineering. No off-the-shelf API handles Tanglish conversationally at production quality.  
---

# 7\. LLM Strategy

## Do You Need a Large Reasoning Model?

Short answer: No, not for most turns.  
A voice agent does not need frontier-level reasoning for every response. The LLM's job in a voice conversation is:

1. Understand intent (classification)  
2. Maintain context (short-term memory)  
3. Generate natural, concise responses (not essays)  
4. Decide when to call tools (structured extraction)  
5. Handle edge cases (escalation, clarification)

## Model Architecture Options

Table

| Architecture | Description | Latency | Cost | When to Use |
| :---- | :---- | :---- | :---- | :---- |
| Small fast model (3B–9B) | Gemma 4 26B, Qwen3, Mistral Small | Very low | Very low | 90% of turns; routine conversation |
| Medium model (20B–70B) | GPT-4.1, Claude Sonnet, Gemini Flash | Low | Moderate | Complex reasoning; multi-step extraction |
| Large model (400B+) | GPT-5.5, Claude Opus, Gemini Pro | Higher | High | Escalation only; edge cases |
| Hybrid routing | Small model handles routine; large model handles complex | Optimized | Optimized | Recommended architecture |
| Speech-to-speech native | GPT-Realtime 2.1, Gemini Live | Low | Very high ($0.09/min) | When single-vendor simplicity matters |

Verified fact: A small open model like Gemma 4 26B costs under $0.0002/min in LLM tokens, while GPT-5.5 at $5 input/$30 output per 1M tokens adds \~$0.015/min — more than an entire cascaded stack with a small model.  
Recommendation: Use a hybrid routing architecture. Route 90% of turns to a fast, cheap small model (Gemma 4, Qwen3, or Mistral Small). Escalate to a larger model only for:

* Ambiguous intent classification  
* Complex structured extraction  
* Sentiment analysis requiring nuance  
* Tool call failures

This reduces both latency and cost by 80%+ without sacrificing quality.

## Deterministic Logic vs. LLM

Not everything needs an LLM:

* Call status tracking (answered, busy, failed) → Deterministic telephony webhook  
* DND scrubbing → Deterministic API call  
* Simple information collection (name, date) → Can use deterministic grammar \+ LLM validation  
* Transcript generation → Deterministic STT output

Use LLMs for language understanding and generation only. Everything else should be deterministic code.  
---

# 8\. Cost Estimation

## Component Cost Breakdown (India, per conversation minute)

Table

| Component | Low-Cost Option | Mid-Range | Premium | Notes |
| :---- | :---- | :---- | :---- | :---- |
| Telephony (India outbound) | ₹0.60 (direct SIP) | ₹0.90 (Exotel/Plivo) | ₹1.50 (Twilio) | Dominant cost at scale |
| STT | $0.0036 (Deepgram Nova-2) | $0.0043 (Deepgram Nova-3) | $0.0075 (AssemblyAI) | Billed per audio minute |
| LLM | $0.0002 (small open model) | $0.002 (GPT-4.1) | $0.015 (GPT-5.5) | Token-based; history matters |
| TTS | $0.003 (Deepgram Aura-2) | $0.005 (Cartesia) | $0.010 (ElevenLabs) | Dominant API cost |
| Orchestration | $0 (DIY) | $0.03 (SigmaMind) | $0.055 (Retell) | Platform fee if used |
| Storage/Recording | $0.001 | $0.002 | $0.005 | S3/Cloudflare R2 |
| Infrastructure | $0.001 | $0.002 | $0.005 | Compute, load balancers |

Verified fact: TTS dominates every cascaded stack at 70–73% of raw component cost. The LLM is under 4% if using a small open model.

## Total Cost Per Minute (All-In)

Table

| Scenario | Cost/Min | Notes |
| :---- | :---- | :---- |
| DIY low-cost stack | \~$0.007–0.015 | Deepgram \+ Gemma 4 \+ Deepgram Aura \+ direct SIP |
| DIY mid-range stack | \~$0.025–0.040 | Deepgram \+ GPT-4.1 \+ Cartesia \+ Exotel |
| DIY premium stack | \~$0.060–0.090 | AssemblyAI \+ GPT-4.1 \+ ElevenLabs \+ Exotel |
| Managed platform (Bland) | \~$0.09–0.14 | All-inclusive; cheapest managed option |
| Managed platform (Retell) | \~$0.13–0.31 | Component-based; transparent |
| Managed platform (Vapi) | \~$0.12–0.25 | $0.05 platform \+ provider costs |
| Speech-to-speech (OpenAI) | \~$0.09 | GPT-Realtime 2.1; single vendor |

## Monthly Cost at Scale (assuming 3 min avg call duration)

Table

| Volume | DIY Low | DIY Mid | Managed (Retell) | Human Agent Equivalent |
| :---- | :---- | :---- | :---- | :---- |
| 100 calls/mo (300 min) | \~$2–5 | \~$8–12 | \~$40–90 | \~$150–300 |
| 1,000 calls/mo (3,000 min) | \~$20–45 | \~$75–120 | \~$400–900 | \~$1,500–3,000 |
| 10,000 calls/mo (30,000 min) | \~$200–450 | \~$750–1,200 | \~$4,000–9,000 | \~$15,000–30,000 |
| 100,000 calls/mo (300,000 min) | \~$2,000–4,500 | \~$7,500–12,000 | \~$40,000–90,000 | \~$150,000–300,000 |

Challenge to your assumption: Human calling in India costs $5–16 per agent hour offshore. At 3-minute calls, a human agent handles \~20 calls/hour \= $0.25–0.80 per call minute in labor alone, plus infrastructure, management, and turnover costs. AI voice agents at $0.07–0.15/min are already cost-competitive, but the gap narrows at lower volumes where human agents can multitask.  
Hidden costs not in the table:

* Barge-in waste: 10–30% extra TTS cost from poor interruption handling  
* LLM history growth: 30-minute calls can 2–3× LLM token costs  
* Minimum commitments: Deepgram Growth requires $4K+/year; ElevenLabs tiers have unused quota waste  
* DLT registration and compliance ongoing costs

---

# 9\. Scalability

## Scaling Scenarios

Table

| Concurrent Calls | Architecture | Bottlenecks | Provider Limits |
| :---- | :---- | :---- | :---- |
| 1 | Single WebSocket thread; local dev | None | N/A |
| 10 | Single server; async event loop | LLM rate limits; TTS concurrency | Most APIs handle 10 easily |
| 100 | Load-balanced workers; Redis for state | Telephony trunk capacity; STT socket limits; LLM TPM | Exotel/Plivo: negotiate CC; Deepgram: concurrency tiers |
| 1,000 | Kubernetes cluster; dedicated SBC; multi-region | Telephony trunk saturation; TTS throughput; database writes | Requires direct SIP or enterprise CPaaS; custom infrastructure |
| 10,000 | Multi-region auto-scaling; direct carrier relationships; edge compute | Carrier-grade routing; regulatory limits; cost explosion | Requires direct Airtel/Jio relationships; dedicated infrastructure |

Technical inference: The primary bottleneck at 100+ concurrent calls is telephony trunk capacity, not AI components. A CPaaS provider will enforce a concurrent-call ceiling. At 1,000 concurrent calls, you need either:

1. Enterprise CPaaS with burst allowances  
2. Direct SIP trunking with multiple carriers  
3. A hybrid approach (primary \+ overflow carriers)

Database consideration: At 100+ concurrent calls, your database must handle high write throughput for call state updates. Use Redis for hot session state (sub-millisecond latency) and PostgreSQL or ClickHouse for persistent call records and transcripts.  
---

# 10\. Indian Telecom/Legal Considerations

## Current Regulatory Framework (2026)

### TRAI TCCCPR Amendment (February 2026\)

Verified fact: TRAI's February 2026 amendment introduced:

1. Mandatory AI disclosure at call opening  
2. Digital Consent Registry — real-time verification before dialing  
3. 140/160 series number segregation — marketing vs. service  
4. Penalties up to ₹10 lakh for violations; repeat offenders face 1-year disconnection and blacklisting

### Specific Requirements for Your Use Case (College Absentee Calling)

Table

| Requirement | Status | Action Needed |
| :---- | :---- | :---- |
| KYC | Mandatory | Business PAN, GST, address proof |
| DLT Registration | Mandatory if any SMS | Entity \+ Header \+ Template registration |
| Telemarketer Registration | Likely required | Register as principal entity with TRAI |
| Consent | Required | Students must have consented to contact (enrollment forms) |
| DND Scrubbing | Mandatory | Scrub against National DND registry |
| AI Disclosure | Mandatory (2026) | Script must disclose AI nature |
| Recording Disclosure | Mandatory | Announce "this call is recorded" |
| Calling Hours | Restricted | 9 AM – 9 PM for most; 9 AM – 7 PM for BFSI |
| Call Log Retention | 1 year | Maintain records |
| Data Protection | DPDPA 2023 applies | Consent withdrawal mechanism; data minimization |

Critical challenge: Your "college absentee" use case sits in a gray area. Is it transactional (educational institution contacting enrolled students about attendance) or commercial (if any survey/data collection beyond immediate academic need)? If transactional, you may use standard DIDs. If commercial/marketing, you need 140-series numbers and explicit consent.  
Do not assume institutional use exempts you. TRAI's regulations apply to all automated calling. The "educational" exemption is narrower than most assume.

### Academic/Student Access

Most providers (Twilio, Exotel, Plivo) offer startup credits but not specific academic discounts for telephony. You can typically get:

* Exotel: 7-day trial with ₹500 credits  
* Twilio: $15–50 trial credit  
* Plivo: Trial credits on request

For significant volume, negotiate as a startup rather than an academic project.  
---

# 11\. English → Telugu Transition

## What Must Change

Table

| Component | English Approach | Telugu Requirement | Gap Severity |
| :---- | :---- | :---- | :---- |
| STT | Deepgram Nova-3 or Whisper | Google Cloud STT or Whisper; custom fine-tuning likely needed | Critical — 15–20% WER on Dravidian languages vs. 5–6% on Indo-Aryan |
| TTS | ElevenLabs/Cartesia/Inworld | VoisLabs, DesiVocal, or Google Cloud | Critical — No premium realtime Telugu TTS exists |
| Endpoint Detection | English-trained models | Needs Telugu acoustic/prosodic training | High — Pauses, fillers, and turn cues differ |
| LLM Prompting | English system prompts | Telugu prompts; code-switching handling | High — Tanglish is not well-handled by any API |
| Pronunciation | Standard English phonemes | Telugu retroflexes, vowel length, sandhi | Critical — Names, places, numbers often mispronounced |
| Regional Dialects | Minor accent variation | Telangana vs. Andhra dialects; regional vocabulary | High — Models trained on standard Telugu |
| Code-Switching | Occasional loanwords | Heavy Tanglish (Telugu \+ English mid-sentence) | Critical — Major unsolved problem |
| Numbers | Standard English number TTS | Telugu number system; lakhs/crores; ordinal forms | Moderate — TTS often falls back to English numerals |
| Names | Standard pronunciation | Telugu names with Sanskrit/Telugu origin; honorifics | High — Critical for your absentee use case |

## The Biggest Technical Gaps

1. Conversational Telugu TTS: Current TTS for Telugu is either robotic (Google Cloud) or not realtime (VoisLabs is batch/streaming hybrid). There is no ElevenLabs-quality Telugu voice that streams with \<200ms latency.  
2. Telugu STT on Phone Audio: Whisper achieves \~20–27% WER on Telugu. On 8kHz phone audio with background noise, this degrades to potentially 30–40% — borderline unusable for information extraction.  
3. Code-Switching: No production API handles Telugu-English code-switching reliably. AssemblyAI's 7.69% WER on code-switching is for major European languages, not Tanglish.  
4. Colloquial Speech: Telugu conversational fillers ("ante," "emito," "inkenti"), discourse markers, and informal grammar are poorly represented in training data.

Recommendation: Do not attempt Telugu until your English system has:

* Proven interruption handling  
* Proven structured extraction accuracy \>90%  
* Proven endpoint detection quality  
* A clear path to custom model fine-tuning

---

# 12\. Competitive Landscape

## Major Players (2026)

Table

| Company | Differentiation | Latency | Voice Quality | Indian Languages | Telephony | Cost | Developer Flex |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Inworld AI | \#1 TTS quality; model-agnostic (220+ LLMs); expressive steering | Sub-200ms | Excellent | 15 GA; 90+ experimental | BYO | Low (cascaded) | High |
| Retell AI | Native telephony; enterprise compliance; structured dialog | \~600ms | Very good | Moderate | Built-in | $0.13–0.31/min | Moderate |
| Vapi | Provider-agnostic orchestration; 14+ providers | Variable | Good (depends on providers) | Depends on providers | BYO | $0.05 \+ providers | High |
| Bland AI | Cheapest at scale; outbound-native; campaign management | Good | Good (below premium) | Limited | Built-in | $0.09–0.14/min | Low |
| Cartesia | Ultra-low latency TTS (\~40ms TTFB); full stack (Sonic \+ Ink \+ Line) | \~40ms TTFB | Very good | 42+ languages | Built-in | $0.06 \+ telephony | Moderate |
| ElevenLabs | Broadest language coverage; voice cloning; ConvAI platform | Sub-100ms | Excellent | 70+ languages | Built-in | Higher | Moderate |
| Bolna AI | Indian/South Asian market focus; INR pricing | Good | Moderate | Indian languages | India-native | $0.05–0.07/min | Moderate |
| OpenAI | Unified ecosystem; Realtime API; SIP connectivity | Low | Good (not premium) | 57+ languages | Built-in | $0.09/min | Low (lock-in) |
| Deepgram | Integrated speech stack; Voice Agent API; turn detection | Low | Good (Aura-2) | 36+ languages | Built-in | $0.05–0.16/min | Moderate |

Verified fact: Bland AI is optimized for high-volume outbound at \~$0.09/minute all-in, making it 30–50% cheaper than Vapi or Retell at scale. Voice quality sits below Vapi/ElevenLabs-based platforms.  
Verified fact: Bolna AI specifically targets Indian/South Asian language markets at $0.05–0.07/min.

## What Differentiates the Strongest Systems

The strongest systems (Inworld, Retell, top-tier custom stacks) differentiate on:

1. Endpoint model quality — Not raw TTS latency, but when to speak  
2. Barge-in recovery speed — \<100ms TTS cancellation  
3. Expressive voice control — Natural pauses, breathing, emotional range  
4. Turn-taking orchestration — Not just fast components, but correct sequencing

Marketing claims vs. reality: Many platforms claim "human-like conversations." In practice, most implementations still feel robotic because:

* They use naive timeout-based endpoint detection  
* They don't handle barge-in gracefully  
* They use cheap TTS that sounds "good enough" in demos but grating over 10+ minutes  
* They don't vary prosody based on conversational context

---

# 13\. Critical Risks

Table

| Risk | Likelihood | Impact | Mitigation |
| :---- | :---- | :---- | :---- |
| Robotic voice | Medium | High | Invest in premium TTS (ElevenLabs/Inworld); use expressive steering; avoid cheap bundled voices |
| High latency | High | High | Edge deploy in India; use small LLM for 90% of turns; optimize turn-taking model |
| Poor interruption handling | High | Critical | This is the \#1 failure mode. Test barge-in aggressively. Budget 10–30% TTS waste. |
| Bad turn detection | High | High | Do not use naive timeouts. Use semantic endpoint detection. |
| Hallucinations | Medium | High | Use deterministic logic for extraction; LLM only for conversation; validation layers |
| Incorrect information extraction | Medium | High | Multi-pass extraction; validation prompts; human review for critical fields |
| Telephone audio degradation | Certain | Medium | 8kHz μ-law is unavoidable; train/test on phone audio specifically; use noise-robust STT |
| Poor Indian accent recognition | Medium | High | Test Deepgram vs. Whisper vs. Google on your target accent; consider fine-tuning |
| Telugu quality | Certain | Critical | No production-ready conversational Telugu stack exists. This is a research project, not a config change. |
| High per-minute costs | Medium | Medium | TTS dominates; negotiate committed tiers; use small LLM; direct SIP at scale |
| Telecom restrictions | Medium | Critical | TRAI can shut down campaigns in 24 hours. Full compliance from day one. |
| Provider lock-in | Medium | Medium | Use modular architecture (Vapi-style or DIY); avoid speech-to-speech native models |
| Concurrency limitations | Medium | High | Negotiate burst allowances; plan for direct SIP at 1000+ concurrent |
| Unreliable connections | Medium | Medium | Multi-carrier failover; retry logic; call quality monitoring |
| Poor scalability | Low | High | Stateless design; Redis for session state; horizontal scaling |
| Privacy/security | Medium | High | DPDPA compliance; encryption; minimal data retention; consent audit trail |

Biggest risk to project success: The combination of poor interruption handling \+ high latency \+ robotic voice creates a death spiral where users hang up immediately. You can have perfect information extraction, but if the conversation feels robotic, nobody will stay on the line long enough to extract anything.  
Second biggest risk: TRAI compliance. A single DND violation or missing AI disclosure can result in number blacklisting, which kills your entire operation.  
---

# 14\. Recommended Technology Strategy

Based on independent research, here are my recommendations. I provide alternatives where appropriate.

## 1\. Best Telephony Provider(s)

Primary recommendation: Exotel

* Best India-native DLT compliance support  
* AgentStream for \<50ms media latency  
* Competitive ₹0.80–1.00/min outbound  
* Strong operational support for Indian regulations

Alternative: Plivo

* Better for globally-minded teams  
* Faster DID provisioning (24–48 hours)  
* Good API quality  
* Slightly weaker India compliance support

Avoid: Twilio for India-specific deployment

* Thinnest DLT support  
* Highest India outbound rates  
* Better suited for global expansion later

At scale (\>20L min/month): Direct SIP with Airtel Business or Jio Business, using Exotel/Plivo as CPaaS layer for API convenience.

## 2\. Best Indian Number Approach

* Start with standard DID numbers from Exotel (not toll-free)  
* Ensure DLT entity registration is complete before any outbound calling  
* Implement AI disclosure in opening script from day one  
* For your college use case, position as transactional/service calls with proper consent documentation  
* Do not use 140-series unless explicitly marketing; standard DIDs or 160-series (if eligible) are appropriate

## 3\. Best STT Approach

Phase 1 (English): Deepgram Nova-3 or Flux

* Fastest streaming latency (\<300ms)  
* Best phone-audio WER among realtime APIs (21.8% on CallHome)  
* Cheapest commercial option ($0.0043/min)  
* Built-in keyterm prompting for names/student IDs

Alternative: Google Cloud STT Chirp 2 if Indian accent recognition proves problematic with Deepgram.  
Phase 2+ (Telugu): Google Cloud STT or fine-tuned Whisper. Deepgram's multilingual accuracy is significantly worse for Dravidian languages.

## 4\. Best TTS Approach

Phase 1 (English): ElevenLabs v3 or Inworld TTS-2

* Highest naturalness and expressiveness  
* Sub-200ms TTFB  
* Good Indian English accent support

Budget alternative: Cartesia Sonic-3.5 (\~40ms TTFB) if latency is absolute priority over expressiveness.  
Phase 2+ (Telugu): This is the hardest gap. Options:

* VoisLabs for batch/pre-recorded Telugu content  
* Google Cloud TTS for basic Telugu (robotic but functional)  
* Custom fine-tuned model (significant research investment)  
* Hybrid: English TTS for English words, Telugu TTS for Telugu words (complex orchestration)

## 5\. Best LLM Strategy

Hybrid routing architecture:

* 90% of turns: Small fast model (Gemma 4 26B, Qwen3 8B, or Mistral Small)  
  * Latency: \<100ms TTFT  
  * Cost: negligible  
  * Handles: routine conversation, simple extraction, status updates  
* 10% of turns: Escalate to GPT-4.1 or Claude Sonnet  
  * Complex ambiguity resolution  
  * Sentiment analysis  
  * Multi-step reasoning  
* Routing decision: Use a lightweight classifier or the small model's confidence score

Avoid: Using GPT-5.5 or Claude Opus for every turn. The cost is 50–100× higher with minimal quality benefit for routine conversation.

## 6\. Best Real-Time Communication Architecture

DIY cascaded pipeline over managed platform for maximum quality control:  
plain  
Telephony (Exotel)   
  → WebSocket/RTP audio stream  
  → VAD \+ Endpoint Detection (semantic, neural)  
  → Streaming STT (Deepgram)  
  → Turn-taking orchestrator  
  → LLM Router (small → large)  
  → Streaming TTS (ElevenLabs/Cartesia)  
  → Audio playback (minimal buffer)  
Key architectural decisions:

* Use WebSockets for full-duplex audio streaming  
* Run semantic VAD (not energy-based)  
* Implement dedicated endpoint detection model  
* Stream everything — no stage waits for previous to finish  
* Maintain separate audio contexts for barge-in recovery  
* Deploy in Mumbai or Bangalore (not US-East)

## 7\. Best Backend Architecture

* Language: Python (FastAPI/Starlette) or Node.js — both have excellent WebSocket support  
* Session state: Redis (hot state, sub-ms latency)  
* Persistent storage: PostgreSQL (call records, transcripts) \+ ClickHouse or BigQuery (analytics)  
* Queue: Redis Streams or RabbitMQ for async processing  
* Orchestration: Custom orchestrator (not a managed platform) — you need control over turn-taking

## 8\. Best Database

* Redis: Call session state, active WebSocket mappings, rate limiting  
* PostgreSQL: User data, campaign configurations, call outcomes, transcripts  
* Object storage (S3/R2): Call recordings, audio artifacts

## 9\. Best Deployment Approach

* Cloud: AWS Mumbai (ap-south-1) or GCP Mumbai (asia-south1)  
* Containerization: Docker \+ Kubernetes for horizontal scaling  
* Edge: Run VAD/STT/endpoint models on edge nodes; LLM/TTS can be API calls  
* Monitoring: Prometheus \+ Grafana for latency percentiles; custom dashboards for barge-in rate, endpoint accuracy, turn-taking latency

## 10\. Best Development Roadmap

Table

| Phase | Duration | Goal | Key Deliverable |
| :---- | :---- | :---- | :---- |
| Phase 0 | 2–3 weeks | Architecture validation | Single-call prototype with Exotel \+ Deepgram \+ GPT-4.1 \+ ElevenLabs |
| Phase 1a | 4–6 weeks | English MVP | Working outbound campaign; basic interruption; structured extraction; transcript |
| Phase 1b | 4–6 weeks | English quality | Semantic endpoint detection; barge-in \<100ms; expressive TTS; \<700ms E2E latency |
| Phase 1c | 4–6 weeks | English scale | 10+ concurrent calls; campaign dashboard; CSV export; basic analytics |
| Phase 2 | 8–12 weeks | Telugu research | Evaluate Telugu STT (Google, Whisper); evaluate Telugu TTS (VoisLabs, Google); build Tanglish test set |
| Phase 3 | 12–16 weeks | Telugu MVP | Basic Telugu conversation; code-switching handling; custom pronunciation |
| Phase 4 | Ongoing | Multilingual | Expand to Hindi, Tamil based on Telugu learnings |

Critical milestone before Phase 2: Your English system must achieve \>90% structured extraction accuracy and \<5% hang-up rate due to robotic feel. If you can't make English feel natural, Telugu will be impossible.  
---

## Final Challenge to Your Core Assumptions

1. "We need a proper Indian number" → Correct, but SIM/eSIM is the wrong approach. Cloud telephony with a DID is the only scalable, legal approach.  
2. "English architecture will automatically produce Telugu" → Dangerously wrong. Telugu requires fundamentally different STT, TTS, endpoint detection, and LLM prompting. Budget 3–4× the English effort.  
3. "Open-source is cheaper" → Not necessarily true. When you factor in GPU costs, engineering time, and ongoing maintenance, commercial APIs are often cheaper for small teams.  
4. "We need a large LLM" → Wrong. A small model with smart routing outperforms a large model on latency, cost, and often user experience.  
5. "The hardest part is making the call" → Wrong. The hardest part is making the conversation feel natural. Telephony is a solved problem; turn-taking is not.  
6. "We can add compliance later" → Catastrophically wrong. TRAI's 2026 regulations can shut you down in 24 hours. Compliance must be in the MVP.

This project is technically feasible and commercially viable, but the path to genuinely natural conversation is steeper than most assume. Start with English, optimize for \<700ms latency and flawless interruption handling, and treat Telugu as a Phase 2 research project with significant custom engineering requirements.

# deepseek approch

# **Independent Research & Architecture Review: AI Voice Calling Platform for India**

Date context: My training data runs through approximately mid-2025. I cannot browse the live web, and the current date in your environment is August 2026\. Where facts may have shifted (pricing, specific Telugu model quality, regulatory changes), I explicitly flag uncertainty. Everything below distinguishes verified fact, provider claim, technical inference, and my recommendation.

---

## **TL;DR / Executive Summary**

1. Do not build the telephony layer from scratch. The highest-leverage decision is to use an Indian CPaaS provider (Exotel or Ozonetel) for Indian DIDs and outbound calling, and either (a) use a managed AI-voice orchestration layer (Vapi, Retell, Sarvam AI) or (b) build your own orchestration on top of Pipecat/LiveKit with best-in-class pluggable STT/TTS. Building your own SIP media server is a distraction.  
2. The quality differentiator is turn-taking and interruption handling, not the LLM. Most "robotic" AI callers fail because of poor VAD/endpointing and slow TTS, not because the LLM is slow. Invest engineering effort there first.  
3. Indian number provisioning is the biggest regulatory/operational friction. Expect KYC, DLT registration, and consent documentation. An individual developer or student cannot easily get a production Indian DID. Partner with a registered entity or use a CPaaS that handles DLT on your behalf.  
4. For English first: Use a streaming STT (Deepgram or Google), a fast LLM (Gemini 2.0 Flash or GPT-4o-mini class), and a streaming TTS (OpenAI TTS, Azure en-IN, or ElevenLabs if budget allows). Target total user-stops-speaking-to-AI-audio-starts under 700ms.  
5. For Telugu later: Do not assume the same pipeline works. You will likely need Sarvam AI or [Gnani.ai](https://gnani.ai/) for STT/TTS because they are Telugu-first and handle code-switching. Realistic Telugu quality depends on these Indian vendors, and you should pilot them in Phase 2 before committing to a single architecture.  
6. Cost per minute: Realistic ₹3–₹15 (USD $0.04–$0.18) depending on TTS choice and scale. This is cheaper than a human telecaller on a per-minute basis, but the comparison is misleading—AI quality still trails humans in difficult conversations.  
7. Biggest risks: KYC/DLT friction, Google Dialer spam-flagging, Telugu TTS naturalness, and user experience of interruptions feeling "too sensitive" or "too stubborn."

---

## **1\. Telephony Options in India**

### **1.1 The Core Distinction: Who carries the call vs. who processes the audio**

You need three things:

* Number (DID): an Indian phone number to call from.  
* Call control API: ability to dial, track status, bridge audio.  
* Real-time audio access: ability to get bidirectional raw audio (typically 8 kHz μ-law PCM for PSTN) into your AI pipeline via WebSocket, SIP/RTP, or proprietary media streams.

The providers below differ primarily in which of the three they actually give you in India.

### **1.2 Comparison of major approaches**

| Provider / Approach | Indian DIDs | Outbound India | Real-time audio to AI | KYC/DLT burden | Concurrency | Notes |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Exotel (Indian CPaaS) | Yes | Yes, strong | WebSocket audio streaming available via "Exotel AI" / "Talk to AI" | Medium — entity KYC; DLT handled | High (hundreds) | Strong India play. Good API. Enterprise-focused. |
| Ozonetel (Kookoo) | Yes | Yes | WebSocket streaming available | Medium | High | Well-documented. More developer-friendly than Exotel historically. |
| Kaleyra (Tata Communications) | Yes | Yes | Media streams available | Medium | Very high | Enterprise. Acquired by Tata in 2024\. Strong on CPaaS but AI-orchestration is less turnkey. |
| Twilio | Limited in India (inbound DIDs discontinued for new accounts; outbound via regulatory bundle) | Yes, via partner carriers | Yes (Media Streams over WebSocket) | High for India numbers; easier via Twilio's global number pool, but those aren't Indian | High | Media Streams are the gold standard for AI integrations, but Indian DID acquisition is painful. |
| Plivo | Yes (Indian DID available) | Yes | Limited AI-specific media stream | Medium | Medium | Solid CPaaS, cheaper than Twilio. AI integrations less turnkey. |
| Sarvam AI (Voice Agent platform) | Partners with Indian telephony | Yes | Fully managed voice pipeline | Medium (they handle much) | Depends on plan | Telugu-first AI voice agents. Strong for Indian languages. Less "bring-your-own-model" flexibility in early versions. |
| [Gnani.ai](https://gnani.ai/) | Partners with carriers | Yes | Managed voice AI | Medium | High | Indian enterprise voice AI. Telugu STT/TTS strong. |
| SIP trunk providers (e.g., Tata, Airtel, enterprise SIP) | Yes | Yes | You must build media server (FreeSWITCH) | High | Very high | Full control, but you own media routing, NAT, codecs, RTP. This is a multi-week engineering effort. |
| SIM/eSIM approach | Uses mobile phone number | Yes, via modem/gateway | Raw audio if you build the modem interface | Very low (just a SIM) | Very low (per SIM) | Not scalable. A SIM can realistically handle 1–3 concurrent calls with poor quality. Using a 4G/5G modem in a server is fragile. |

### **1.3 SIM/eSIM vs. virtual numbers vs. SIP — what's actually appropriate?**

Technical inference (strong): A normal SIM/eSIM in a phone or USB modem is not appropriate for a calling platform. Limitations:

* Mobile network operators often block or degrade concurrent voice calls on consumer SIMs. A standard SIM supports at most 2–4 simultaneous voice calls, and call quality over a relayed modem is poor.  
* You'd be building your own GSM stack, which is a massive detour from the actual value (conversation quality).  
* Caller ID would be a personal mobile number, which looks legitimate but doesn't scale and creates personal liability.

Recommendation: Use cloud telephony with Indian DIDs via a CPaaS. This gives you proper concurrency, call control, and regulatory compliance without the fragile hardware path.

### **1.4 The "AI-voice-agent platform" shortcut**

Providers like Vapi, Retell AI, LiveKit, and Bolna abstract the entire telephony+AI pipeline. They each have different India coverage:

* Vapi: Works with Twilio/Telnyx/Exotel; Indian DID support depends on the underlying provider. Vapi handles WebSocket audio, VAD, STT/TTS plugin, LLM orchestration, and structured data extraction. Fast to start.  
* Retell AI: Strong turn-detection model. Telephony via Twilio/Vonage/SIP. Indian DIDs possible via Plivo/Exotel connector.  
* LiveKit: Open-source WebRTC/agents framework. You bring your own telephony via SIP; stronger for building custom pipelines.

Key inference: If your goal is to get a high-quality English demo fast, using a managed orchestrator (Vapi/Retell) with an Indian CPaaS for numbers is the pragmatic path. If you need deep control over turn-taking (which you said is a differentiator), you may eventually build your own orchestrator, but do not start there.

---

## **2\. Real-Time Voice Architecture: Critical Components**

### **2.1 The pipeline**

`text`

`User speaks`  
   `↓`  
`PSTN → Provider (SIP/RTP) → Audio stream (WebSocket/PCM)`  
   `↓`  
`VAD / Endpoint detection`  
   `↓`  
`Streaming STT (interim hypotheses)`  
   `↓`  
`Conversation orchestrator (state machine + LLM)`  
   `↓`  
`TTS (streaming first-chunk)`  
   `↓`

`Audio back into provider`

### **2.2 Component-by-component analysis**

| Component | Role | Impact on perceived quality | Notes |
| :---- | :---- | :---- | :---- |
| VAD (Voice Activity Detection) | Detect whether there is speech energy in the audio | Very high | Bad VAD causes either clipped speech or long silences. Use adaptive thresholds, not fixed energy. |
| Endpoint detection | Decide when the user has finished their turn | Extremely high | This is the \#1 source of "robotic" feel. Pure silence threshold fails for hesitation. Need semantic-aware endpointing. |
| STT (Streaming) | Convert speech to text, emit interim results | High | Use interim results to start LLM pre-warming. Accuracy of Indian English matters. |
| Turn-taking model | Decide who speaks when | Extremely high | Should incorporate VAD, syntax, semantics, and user speaking style. Some vendors (Retell) sell this as a service. |
| Barge-in / interruption | Stop TTS when user starts speaking | Very high | Must stop within \~50–150ms of user speech onset. Full-duplex audio is mandatory. |
| LLM | Generate response, track state, extract entities | Medium (for quality) | A slow LLM adds latency; a wrong LLM fails extraction. But the LLM is rarely the quality bottleneck if chosen correctly. |
| TTS (Streaming) | Produce speech from text | Very high | First-audio latency matters most. Naturalness, pacing, and sentence endings matter for trust. |
| Session memory | Maintain context, slots, user intent | Medium | Use Redis for ephemeral state \+ Postgres for results. Keep context window tight. |
| Tool/function calling | Query knowledge base, validate data, update DB | Medium | Keep tools fast; avoid synchronous API calls that block the turn. |
| Call state machine | Track dialing, ringing, in-progress, completed | Medium | Finite-state machine, not ad-hoc code. |

### **2.3 Largest perceived-quality levers (my inference)**

1. Endpoint detection quality — decides whether the AI waits awkwardly or interrupts too early.  
2. TTS first-audio latency and naturalness — the most audible difference.  
3. Barge-in sensitivity — too sensitive \= AI stops at coughs; too stubborn \= feels like IVR.  
4. STT accuracy on Indian English — mis-recognition cascades into wrong responses.  
5. LLM speed — less important than people think if you pre-warm with interim STT.

---

## **3\. Latency Targets and Pipeline Analysis**

### **3.1 What humans perceive**

* Human turn-taking gap in phone conversations: \~150–400ms.  
* Below \~500ms total system response feels "good"; below \~700ms is acceptable; above \~1000ms feels robotic.

### **3.2 Complete latency chain (user stops speaking → AI audio starts)**

| Stage | Typical (naive) | Optimized | How to optimize |
| :---- | :---- | :---- | :---- |
| User stops speaking → VAD detects silence | 150–300ms | 50–150ms | Shorter silence threshold, adaptive VAD, or semantic endpointer |
| VAD → STT final hypothesis | 200–500ms | 100–300ms (interim) | Use interim hypotheses; don't wait for full final |
| STT → LLM prompt | 0–50ms | 0 | Pre-assemble prompt |
| LLM → first response token | 300–2000ms | 200–500ms | Use fast model (Gemini Flash, GPT-4o-mini), streaming |
| LLM → TTS first audio | 100–500ms | 30–150ms | Streaming TTS; first-chunk synthesis |
| TTS audio → user's ear | 20–100ms (PSTN jitter) | 20–100ms | Provider-dependent |
| Total | 770–3450ms | 400–1200ms |  |

### **3.3 Where naive systems fail**

Verified fact: The single biggest mistake is waiting for STT final result before calling the LLM. Final results are delayed by the trailing silence detector. High-quality systems use interim STT hypotheses to begin generating a response, then revise if the final hypothesis changes.

Technical inference: Another major source of latency is using a non-streaming TTS. Requesting the entire audio file from TTS before playback starts adds 500ms–2s. Streaming TTS with chunked synthesis is mandatory.

### **3.4 Practical target (my recommendation)**

* English demo: Total user-stops-speaking → AI audio starts: 600–800ms.  
* English production: 500–700ms.  
* Telugu: Expect \+100–200ms due to STT/TTS maturity, at least initially.

---

## **4\. Interruption and Turn-Taking**

### **4.1 Why this is the \#1 hard problem**

Turn-taking is about predicting intent, not just detecting sound. Humans use syntax, prosody, and semantics to know when the other person has yielded the floor. A purely energy-based VAD cannot do this.

### **4.2 The sub-problems**

| Problem | Naive approach | Better approach |
| :---- | :---- | :---- |
| User interrupting AI | Stop TTS when VAD detects user speech | Full-duplex audio; stop TTS within 50–150ms; do not stop on single-frame noise |
| User pauses while thinking | Treat as end of turn | Use longer silence threshold \+ semantic endpointer that checks if the utterance is a complete thought |
| Incomplete sentences | Respond immediately | Wait for syntactic completion or timeout; let LLM decide if the user trails off |
| Simultaneous speech | Just stop TTS | Consider both audio streams; if AI has almost finished a sentence, let it complete; if early in utterance, stop |
| Background speech / TV | Stop TTS and get confused | Use robust VAD \+ speaker separation; require sustained energy above threshold for N ms |
| False interruption (cough, uh) | Stop TTS | Require sustained user speech (e.g., 100ms) before interrupting; re-synthesize TTS from cut point |
| Long pauses | Timeout and prompt user | Adaptive timeouts; AI can say "Are you still there?" rather than restarting the whole turn |
| Agent deciding when to respond | Fixed silence threshold | Semantic turn-taking: use an LLM or dedicated model to judge if the user's utterance is complete |

### **4.3 Architectural patterns used by high-quality systems**

1. Full-duplex audio — The system listens while speaking. This is non-negotiable. (Twilio Media Streams, Exotel WebSocket, Pipecat, LiveKit all support this.)  
2. Continuous VAD with hysteresis — A short "debounce" window prevents false triggers. Example: user speech must exceed threshold for 80–120ms before AI stops TTS.  
3. Semantic endpointing — A small classifier (or the main LLM) decides "is the user done?" based on the content of the interim transcript, not just silence. Retell AI's turn-detection model does this; you can also prompt the LLM: "Is this utterance complete? Answer only YES/NO."  
4. TTS cut-point recovery — When interrupted, remember the last word boundary; resume from a natural sentence boundary rather than replaying the whole response.  
5. Interrupt patience parameter — Different contexts need different sensitivity. A college absence call should be more patient than a sales call. Expose this as a tunable parameter.

### **4.4 My recommendation**

Do not rely solely on a vendor's default turn detection. Even if you use Vapi/Retell, test with real Indian English audio containing hesitation, code-switching, and background noise and tune:

* Silence threshold (e.g., 400–600ms for Indian English)  
* Interrupt activation time (e.g., 100–150ms of sustained user speech)  
* Semantic endpointing on/off

This tuning is where your project will win or lose.

---

## **5\. TTS Landscape (2024–2025 snapshot, flag for 2026 changes)**

| TTS | Naturalness | Streaming | First-audio latency | English Indian accent | Telugu | Cost (indicative) | Verdict |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| ElevenLabs | Very high | Yes | \~200–400ms | Good en-IN voices | Yes, but quality uncertain for conversational Telugu | \~$0.30/1k chars (Turbo) | Best naturalness, highest cost. Use for English demo if budget allows. |
| OpenAI TTS (tts-1 / GPT-4o-mini-tts) | High | Yes | \~100–300ms | Good | Telugu supported, mixed quality | \~$15/1M chars | Best price/quality for English. Good first choice. |
| Azure Neural TTS | Good | Yes | \~100–300ms | Excellent en-IN voices (Neerja, Arjun) | te-IN (Shruti, Mohan) decent | \~$16/1M chars | Solid, reliable, good Indian English. Slightly less "warm" than ElevenLabs/OpenAI. |
| Google Cloud TTS | Good | Yes | \~100–300ms | Good en-IN | te-IN available | \~$16/1M chars | Similar to Azure. |
| Cartesia (Sonic) | High | Yes | Very low (\<150ms) | Good | Telugu growing | Tiered | Very low latency, strong for real-time. Check Telugu maturity in 2026\. |
| Sarvam AI TTS | Good (Telugu-first) | Yes | Low | Good | Strong Telugu | Per-char, India pricing | Best Telugu option as of my knowledge. English is decent but not best-in-class. |
| [Gnani.ai](https://gnani.ai/) TTS | Good | Yes | Low | Good | Strong Telugu | Enterprise pricing | Solid Indian language option. |
| Open-source (VITS, XTTS v2, Kokoro, etc.) | Variable | Some | Variable | Variable | Poor Telugu mostly | Compute cost | Not recommended for Telugu initially. XTTS v2 can be fine-tuned but engineering cost high. |

### **5.1 Key inferences**

* For English Phase 1: OpenAI TTS or Azure en-IN give the best cost/quality tradeoff. ElevenLabs is noticeably more natural but 20x more expensive per character. The difference matters when you scale.  
* For Telugu Phase 2: The gap between open/global providers and Sarvam/Gnani is significant. Plan to switch TTS vendor for Telugu rather than assuming ElevenLabs/OpenAI will handle conversational Telugu well.  
* Indian English accents: Azure en-IN voices are specifically trained on Indian English. OpenAI TTS handles Indian English well but is less India-specific. Test both with your actual scripts.

---

## **6\. STT Landscape (2024–2025 snapshot)**

| STT | Streaming | Indian English | Telugu | Code-switching | Latency | Cost (indicative) |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Deepgram (Nova-3) | Yes | Very good | Yes (but quality varies) | Some | Very low | \~$0.0059/min |
| Google Cloud STT | Yes | Good | Good (te-IN) | Some | Low | \~$0.016/min |
| Azure STT | Yes | Very good (en-IN) | Good (te-IN) | Some | Low | \~$0.015/min |
| AssemblyAI (Universal) | Yes | Good | Yes | Moderate | Low | \~$0.0025/min |
| OpenAI Whisper (API) | Batch (chunking needed) | Very good | Good | Some | Higher | \~$0.006/min |
| Sarvam AI STT | Yes | Good | Best Telugu | Strong code-switching | Low | India pricing, competitive |
| [Gnani.ai](https://gnani.ai/) STT | Yes | Good | Strong Telugu | Strong | Low | Enterprise |
| Nvidia Canary (open) | Yes (with setup) | Good | Good | Moderate | Depends on GPU | Compute cost |

### **6.1 Key inferences**

* For English Phase 1: Deepgram or Google STT are the safe choices. Deepgram is cheaper and lower-latency; Google is very accurate on Indian English. Both stream well.  
* For Telugu Phase 2: Sarvam AI or [Gnani.ai](https://gnani.ai/) are the realistic best options. Their models are trained on Indian telephone speech and handle code-switching better than the global providers. Pilot Sarvam in Phase 1 for English-to-Telugu comparison.  
* Telephone audio (8kHz) degrades STT accuracy for all systems. Ask your telephony provider for 16kHz audio passthrough if possible. If not, choose an STT that explicitly trains on telephony audio (Deepgram, Google, Sarvam, Gnani).

---

## **7\. LLM Strategy**

### **7.1 Do you need a large reasoning model?**

No. This is one of your assumptions I want to challenge.

A voice agent for structured calls (absence follow-up, lead qualification, appointment scheduling) is not a task that requires deep reasoning. The LLM needs to:

* Understand conversational intent from noisy STT output  
* Decide what to say next from a constrained set of behaviors  
* Extract structured entities (name, reason, return date)  
* Stay within policy boundaries (don't promise things, don't hallucinate)

These are achievable with small, fast models.

### **7.2 Model comparison**

| Model class | Latency | Cost | Strengths | Weaknesses |
| :---- | :---- | :---- | :---- | :---- |
| Large reasoning (o1/o3, Sonnet 3.7+) | 1–5s first token | High | Complex reasoning, long-horizon tasks | Massive latency, expensive, overkill for calls |
| Large general (GPT-4o, Claude Opus) | 300–800ms | Medium-high | Good quality, strong tool use | Still overkill for most call flows |
| Small/fast (Gemini 2.0 Flash, GPT-4o-mini, Llama 3.1 8B on Groq) | 100–500ms | Low | Low latency, cheap, sufficient for slot-filling and conversational control | May struggle with very complex user queries |
| Local (Llama 3.x 8B, Qwen 2.5 7B) | 100–500ms (with GPU) | Very low marginal | Privacy, low cost at scale | DevOps burden, lower quality than cloud fast models |
| Deterministic logic | 0ms | Zero | Perfect for validation, formatting, state transitions | Cannot handle open-ended natural language |

### **7.3 Hybrid architecture (my recommendation)**

`text`

`Call flow:`  
`1. Deterministic state machine handles dial, greeting, retry, hangup`  
`2. LLM (small/fast) handles natural language:`  
   `- Understand user utterance`  
   `- Decide intent (e.g., "gives reason", "asks question", "wants to reschedule")`  
   `- Extract entities (name, reason, date)`  
   `- Generate the next response`  
`3. Deterministic validators check the LLM's extraction:`  
   `- Is the reason in an allowed enum? If not, ask LLM to re-classify`  
   `- Is the date valid? If not, ask again`

`4. Structured output is stored via a separate, deterministic Pydantic schema`

This reduces hallucination risk and speeds up extraction.

### **7.4 The hallucination challenge**

Technical inference (high confidence): LLMs will hallucinate names, numbers, and commitments in a voice call unless you constrain them. Mitigations:

* Use JSON-schema / function-calling output rather than free text for structured data.  
* Validate numbers against known formats (phone, dates).  
* Keep a "ground truth" list of allowed entities in the system prompt (e.g., student name must match the CSV record).  
* Use a separate small LLM call to verify extracted facts.

---

## **8\. Cost Analysis**

### **8.1 Per-minute cost breakdown (English, moderate quality)**

| Component | Cost basis | ₹/min (approx) | $/min |
| :---- | :---- | :---- | :---- |
| Telephony (Indian outbound, mobile) | ₹0.30–₹1.00/min at moderate volume | ₹0.30–₹1.00 | $0.004–$0.012 |
| Number rental | ₹500–₹2000/month amortized | ₹0.01–₹0.05 | negligible |
| STT | Deepgram \~₹0.50/min; Google \~₹1.30/min | ₹0.40–₹1.30 | $0.005–$0.016 |
| LLM | Gemini Flash / GPT-4o-mini: 2–5k in \+ 0.5–1k out tokens/min | ₹0.20–₹1.00 | $0.002–$0.012 |
| TTS (OpenAI/Azure) | \~₹1.30/1k chars; AI speaks \~400 chars/min | ₹0.50–₹0.80 | $0.006–$0.010 |
| TTS (ElevenLabs) | \~₹25/1k chars | ₹10–₹15 | $0.12–$0.18 |
| Infra \+ storage \+ DB | Redis, Postgres, compute, S3 per call | ₹0.10–₹0.50 | $0.001–$0.006 |
| Total (budget TTS) |  | ₹1.51–₹4.65 | $0.018–$0.056 |
| Total (premium TTS) |  | ₹11–₹18.65 | $0.13–$0.22 |

### **8.2 Scale estimates**

Assumptions: average call duration 2 minutes; average connect rate 50–60% for outbound.

| Monthly calls | Minutes (connected) | Cost (budget) | Cost (premium) |
| :---- | :---- | :---- | :---- |
| 100 | \~200 | ₹300–₹930 | ₹2,200–₹3,730 |
| 1,000 | \~2,000 | ₹3,020–₹9,300 | ₹22,000–₹37,300 |
| 10,000 | \~20,000 | ₹30,200–₹93,000 | ₹2.2L–₹3.7L |
| 100,000 | \~200,000 | ₹3.0L–₹9.3L | ₹22L–₹37L |

### **8.3 vs. human calling**

A human telecaller in India costs ₹15,000–₹25,000/month. At 160 working hours/month and 60% talk time, that's \~5,760 minutes → ₹2.6–₹4.3/min. But a human can handle only 1 call at a time, needs breaks, training, and supervision.

My inference: AI is cost-competitive at scale, especially with budget TTS. But the quality gap matters more than cost for your project's stated goal. Do not optimize for cost first; optimize for quality, then reduce cost.

---

## **9\. Scalability**

### **9.1 Concurrency bottlenecks**

| Scale | Bottleneck | Solutions |
| :---- | :---- | :---- |
| 1 call | Development comfort | Manual testing |
| 10 calls | Single-threaded orchestration, provider API rate limits | Horizontal orchestration workers, use async I/O (Python asyncio, Node.js) |
| 100 calls | STT/TTS API rate limits; LLM concurrency; audio websocket management | Use streaming providers with high rate limits; provision more API keys; use connection pooling |
| 1000 calls | Telephony provider concurrency caps; SIP trunk capacity; CPU for media processing | Multi-provider telephony; dedicated SIP trunk; use managed media servers (Asterisk/FreeSWITCH cluster) |

### **9.2 Architecture for scale**

* Stateless orchestration workers that consume a queue of "call sessions." Each active call is a WebSocket connection held by a worker.  
* Redis for session state (transcript buffer, slot values, conversation history).  
* PostgreSQL for final results, campaign state, exports.  
* Queue (RabbitMQ/Kafka or Redis streams) for call commands: dial, hangup, retry.  
* Media server only if you're doing SIP directly; if using CPaaS WebSocket, you skip this entirely.

Technical inference: For 1,000 concurrent calls, the cost of compute alone is manageable, but provider rate limits for STT/TTS/LLM will be the real constraint. You will need enterprise quotas with Deepgram/Google/OpenAI and possibly multiple API keys. Also, Indian CPaaS providers have per-account concurrency caps that may require negotiation.

---

## **10\. Indian Telecom/Legal Considerations**

### **10.1 KYC for Indian DIDs**

Verified fact (as of 2025, likely unchanged 2026): To obtain a virtual Indian number (DID) for outbound calling, you must complete KYC. Requirements typically:

* Registered entity (company, LLP, partnership, sole proprietorship) — or individual KYC with some providers (harder)  
* PAN card of entity/individual  
* Address proof  
* GST certificate if entity  
* Authorized signatory documentation

Technical inference: An individual student developer will struggle. The pragmatic path is:

1. Partner with the college/institution as the KYC entity, or  
2. Use a provider's sandbox/shared number for development (limited), or  
3. Use a reseller that handles KYC on your behalf (many CPaaS resellers exist, but trust is an issue).

### **10.2 DLT (Distributed Ledger Technology) registration**

Verified fact: TRAI's TCCCPR 2018 (amended) requires commercial communicators to register on DLT platforms (operated by Jio, Airtel, Vi, BSNL). This applies to SMS and voice commercial communications. Requirements:

* Entity registration on the DLT portals  
* Header registration (for SMS) — for voice, this maps to caller ID registration  
* Content template registration (for voice: call scripts/intent templates may need approval)  
* Consent management: consent from recipients must be captured and logged  
* Penalties for non-compliance, including number disconnection

Technical inference: The category matters:

* Transactional calls (related to an existing relationship, e.g., college notifying its own student about absence) have lighter consent requirements than promotional calls.  
* A college calling its enrolled student about attendance is likely transactional, but the college should still have the student's consent (e.g., via admission forms) and maintain records.  
* Some CPaaS providers (Exotel, Ozonetel) handle DLT registration as part of onboarding. Use them.

### **10.3 Recording and privacy**

Verified fact: Indian law (IT Act, Indian Telegraph Act) requires that if you record calls, you must inform the other party and/or obtain consent. A standard practice is to play a short announcement: "This call is being recorded for quality and training purposes."

Technical inference (strong): You should do this for your prototype too. It reduces legal risk and sets user expectations. The DPDP Act 2023 (Digital Personal Data Protection Act) is in effect with rules being finalized; it requires consent for processing personal data, data minimization, and breach notification. This applies to storing transcripts, names, phone numbers, etc.

### **10.4 Automated calling restrictions**

Verified fact (as of 2025): India does not have a blanket ban on automated outbound calls like the US TCPA. However:

* TRAI's DND registry allows users to opt out of promotional calls.  
* Since 2024, Google Dialer on Android flags suspected spam numbers. Many shared cloud-telephony numbers get flagged, which destroys trust.  
* TRAI has been increasingly concerned about AI voice calls; there were discussions in 2024–2025 about mandating disclosure of AI callers ("I am an AI assistant").  
* In late 2024, Airtel and Jio launched their own AI voice services, so the direction is toward more AI calls, not fewer, but with disclosure expectations.

My recommendation: For the college absence use case:

1. Ensure the college has student consent (admission form).  
2. Classify as transactional, not promotional.  
3. Disclose AI nature at the start ("This is an AI assistant from \[College\] calling regarding your attendance.").  
4. Play a recording notice.  
5. Use a dedicated Indian DID with clean reputation, not a shared pool number.

---

## **11\. English → Telugu Transition**

### **11.1 What changes**

| Component | English Phase 1 | Telugu Phase 2 | What breaks |
| :---- | :---- | :---- | :---- |
| STT | Deepgram/Google en-IN works well | Sarvam/Gnani preferred | Global STT struggles with casual Telugu; code-switching is the killer |
| TTS | OpenAI/Azure/ElevenLabs | Sarvam/Gnani strongly preferred | Global TTS often has unnatural Telugu prosody; names and numbers garbled |
| LLM prompt | English system prompt | Telugu system prompt \+ transliteration policies | Hallucination risk higher; need Telugu-native constraint validation |
| Entity extraction | English NER works | Indian names/places/dates in Telugu are hard; use Telugu-specific validators | Date/time formats, student names in Telugu script |
| Turn-taking | Tuned for English prosody | Telugu has different pause patterns; retune VAD/endpointing | English tuning won't transfer |
| Code-switching | Minor | Major — Telugu speakers mix English words (Tanglish/Tenglish) | STT must handle both scripts in same utterance |
| Phone audio | 8kHz degrades less | 8kHz degrades Telugu more because of retroflex and aspirated sounds | Telugu recognition on PSTN is measurably worse |
| Locale handling | Simple | Andhra vs Telangana dialects, formal vs colloquial register | Regional variation in greetings, pronouns, verb endings |

### **11.2 Biggest Telugu technical gaps (my inference, 2025 knowledge)**

1. Conversational Telugu TTS — Global providers have Telugu, but it's often news-reading register, not conversational. Sarvam/Gnani are better but still maturing for "natural human phone conversation" quality.  
2. Code-switching STT — Very few models handle "I am going to college, na? Actually, sir, nenu absent ayyi...". Sarvam is the strongest I know of.  
3. Telugu entity extraction — Extracting dates ("repu", "nellu", "varam"), names, and locations from colloquial Telugu requires Indian-specific training data.  
4. Phone audio degradation — Telugu has retroflex consonants (ట, ఠ, డ, ఢ, ణ) and aspirated stops that are poorly represented at 8kHz. Demand 16kHz audio from your telephony provider.

### **11.3 Phase 2 recommendation**

Run a Telugu pilot early. Do not assume the English architecture transfers. In Phase 1 (English), already sign up for Sarvam AI's sandbox and test a small Telugu script. This will reveal:

* Whether your telephony provider can deliver 16kHz audio for Telugu  
* Whether Sarvam's STT handles your target dialect  
* Whether the TTS is acceptable to native Telugu speakers

Budget this pilot as a separate line item.

---

## **12\. Competitive Landscape**

### **12.1 Who's doing high-quality AI phone conversations (as of 2025\)**

| Player | Focus | Strengths | Weaknesses |
| :---- | :---- | :---- | :---- |
| Retell AI | Developer platform, real-time AI voice agents | Strong turn-detection model, low latency, telephony integration, good dev UX | Less India-specific; Indian number support depends on underlying providers |
| Vapi | Developer platform | Large ecosystem, flexible "bring your own" STT/LLM/TTS, telephony handled | More configuration burden; India quality depends on providers |
| ElevenLabs Conversational AI | Voice agent platform | Top-tier TTS, brand, naturalness | Costly; less telephony depth in India; Telugu uncertain |
| OpenAI Realtime API | Voice-native API | Multimodal speech-to-speech, low-latency, high quality English | Expensive; telephony is DIY; Telugu uncertain; compliance burden on you |
| Google Gemini Live API | Voice-native API | Fast, good multilingual, competitive pricing | Telephony is DIY; developer docs evolving; Telugu quality unclear |
| Sarvam AI | Indian voice agents, Telugu-first | Best Telugu STT/TTS, India telephony partnerships, code-switching | Smaller ecosystem, less global tooling; English not as polished as global players |
| [Gnani.ai](https://gnani.ai/) | Indian enterprise voice AI | Strong Indian language models, enterprise trust, regulated industries | Less developer-friendly, more sales-led |
| LiveKit \+ Pipecat (open source) | Infrastructure | Maximum control, WebRTC/SIP, real-time agents | You assemble everything; no turnkey India telephony; engineering-heavy |
| Twilio \+ Voice Intelligence | CPaaS \+ AI add-ons | Mature telephony, Media Streams, developer trust | Indian DID friction; AI add-ons less flexible than dedicated platforms |
| Cisco/Genesys/AWS Connect | Enterprise contact center | Scale, compliance, integration | Not for a startup prototype; cost and complexity |

### **12.2 What differentiates the strongest systems (my analysis)**

1. Turn-detection model quality — Retell's biggest moat is their endpointer. This is where most DIY systems fail.  
2. TTS naturalness \+ latency — ElevenLabs's voice quality is a real differentiator; Cartesia's low latency is too.  
3. Indian language support — Sarvam and Gnani own Telugu for now. Global players are behind in code-switched Indian speech.  
4. Telephony partnership depth — Exotel/Ozonetel have the Indian carrier relationships; a US-based platform (Vapi/Retell) without a local partner will struggle with Indian DIDs.  
5. Developer flexibility — Vapi and LiveKit allow swapping STT/LLM/TTS; closed platforms (Sarvam, Gnani) don't, but deliver quicker for Indian languages.

### **12.3 My inference about the 2026 landscape**

By mid-2026, expect:

* OpenAI Realtime API and Gemini Live API to have more telephony partners, but India DID support still gated by local KYC.  
* Sarvam/Gnani expanding English quality, but still Telugu-first.  
* More hybrid platforms (e.g., Vapi \+ Sarvam connectors) emerging.  
* TRAI rules on AI call disclosure possibly formalized.

---

## **13\. Critical Risks (Challenging Your Project)**

### **13.1 Top risks ranked by severity**

| Risk | Likelihood | Impact | Mitigation |
| :---- | :---- | :---- | :---- |
| KYC/DLT friction prevents you from getting an Indian DID | High | Project-stopper | Partner with the college entity; use Exotel/Ozonetel who handle DLT; start this immediately |
| Google Dialer flags your number as spam | Medium-High | Trust destroyed | Dedicated DID, keep call volumes moderate per day, disclose AI identity, avoid repeated short calls |
| Robotic feel due to endpoint detection | High | Quality fails | Invest heavily in turn-taking tuning; consider Retell's endpointer or semantic endpointing |
| Telugu TTS quality is not human-natural | Medium-High | Phase 2 fails | Pilot Sarvam/Gnani early; budget for model fine-tuning or hybrid TTS |
| STT mis-recognizes Indian English on 8kHz telephone audio | Medium | Data extraction wrong | Use telephony-trained STT; request 16kHz audio; use deterministic validators |
| TTS cost blows budget at scale | Medium | Commercial failure | Start with OpenAI/Azure TTS; reserve ElevenLabs for demo only |
| LLM hallucination during information extraction | Medium | Wrong results, reputation damage | Use function-calling/JSON schema \+ deterministic validators; log and audit |
| Provider lock-in | Medium | Flexibility loss | Abstract STT/TTS/LLM behind interfaces; keep telephony provider swappable |
| Concurrency limits on STT/TTS/LLM APIs | Low-Medium | Scale ceiling | Provision multiple keys, negotiate enterprise quotas |
| Privacy/DPDP violation | Medium | Legal risk | Anonymize after export; store transcripts with consent; implement data minimization |
| Telephony audio degradation | Medium | Quality fails | Test with real PSTN calls; ask provider for 16kHz passthrough |
| User hangs up on AI | High (practical) | Campaign fails | Short, clear scripts; disclose AI; offer opt-out |

### **13.2 Three assumptions I want to challenge**

1. "Authentication and authorization are not required initially." — True for your web dashboard, but false for telephony. Indian number KYC/DLT is mandatory regardless of your dashboard. Do not defer this.  
2. "English first, Telugu later is a smooth transition." — The English architecture will not automatically transfer. The gap between English and conversational Telugu in STT/TTS/entity-extraction is large. Treat Telugu as a separate project with its own pilot.  
3. "We should build the whole pipeline ourselves for differentiation." — Your stated differentiator is conversation quality, not infrastructure. Building your own SIP/media server is weeks of work that does not improve conversation quality. Use proven platforms for telephony and audio transport; focus your engineering on turn-taking, prompt design, extraction validation, and language quality.

---

## **14\. Recommended Technology Strategy**

### **14.1 Guiding principles**

1. Highest conversation quality per engineering hour.  
2. Indian telephony credibility (DID, DLT, spam-free).  
3. Switchable components (STT/TTS/LLM) to avoid lock-in.  
4. Phase 2 Telugu readiness.

### **14.2 Recommendations**

#### A. Telephony provider(s)

Primary: Exotel or Ozonetel (Indian CPaaS with WebSocket streaming and DLT assistance).

* Both offer Indian DIDs, outbound dialing, and real-time audio streaming suitable for AI integration.  
* Exotel's "Exotel AI" suite is more mature for voice agents; Ozonetel is more developer-friendly.  
* Choose based on: WebSocket audio format, pricing, concurrency, and whether they can provide 16kHz audio.

Alternative: Plivo (cheaper, Indian DID available) if you want a global CPaaS.

Avoid for initial phase: Twilio (Indian DID friction), SIP direct (engineering burden), SIM-based (unscalable).

#### B. Indian number approach

* Use a dedicated Indian mobile DID from your CPaaS.  
* Complete KYC through the college or a registered entity.  
* Ask the CPaaS to handle DLT registration for transactional calls.  
* Disclose AI identity in the greeting.

#### C. STT

* English Phase 1: Deepgram (low cost, low latency) or Google STT (high accuracy for Indian English). Test both with your actual audio.  
* Telugu Phase 2: Sarvam AI STT (Telugu-first, code-switching) or [Gnani.ai](https://gnani.ai/).

#### D. TTS

* English Phase 1: OpenAI TTS (tts-1 or gpt-4o-mini-tts) for cost/quality; Azure en-IN (Neerja/Arjun) if you prefer stronger Indian English; ElevenLabs only for investor demos.  
* Telugu Phase 2: Sarvam AI TTS or [Gnani.ai](https://gnani.ai/) TTS. Do not rely on global providers for Telugu.

#### E. LLM strategy

* Primary: Gemini 2.0 Flash or GPT-4o-mini (fast, cheap, streaming, function-calling).  
* Fallback: Groq-hosted Llama 3.x 70B for low-latency open-source option.  
* Deterministic layer: Python/Pydantic validators for entity extraction, date parsing, and state transitions. The LLM generates natural language; validation is deterministic.

#### F. Real-time communication architecture

Option 1 (recommended for speed): Use Vapi or Retell AI as the orchestration layer. Configure your chosen STT/TTS/LLM. Connect to your Indian CPaaS for DIDs. Focus on prompt design and turn-tuning.

Option 2 (recommended for control): Build orchestration on Pipecat (Python) or LiveKit Agents. Connect to CPaaS WebSocket. Implement your own VAD/endpointing with semantic checks. This is more work but gives you full control over turn-taking and interruption.

Option 3 (not recommended initially): Build everything on FreeSWITCH \+ custom media server.

#### G. Backend architecture

* Language: Python (FastAPI) or TypeScript (Node.js). Python preferred for AI ecosystem.  
* Orchestrator: Async service per active call (Pipecat actor model, or FastAPI \+ asyncio WebSockets).  
* Queue: Redis Streams or RabbitMQ for call commands.  
* Session state: Redis (with TTL) for live call context.  
* Database: PostgreSQL for campaigns, contacts, results, transcripts.  
* Object storage: S3-compatible (AWS S3 or MinIO) for audio recordings and full transcripts.  
* Export: Generate Excel/CSV via backend job; use `openpyxl` or similar.

#### H. Best deployment approach

* Containerize services (Docker).  
* Deploy orchestration workers on AWS/GCP/Azure (or an Indian cloud provider like E2E/Netmagic for data residency).  
* Use managed Redis and Postgres for low ops overhead.  
* For high concurrency, auto-scale workers horizontally.

#### I. Development roadmap

Phase 0 (2–4 weeks): Telephony setup.

* Choose CPaaS, complete KYC, get Indian DID, test outbound call.  
* Set up WebSocket audio streaming and record a sample call.

Phase 1 (4–6 weeks): English MVP.

* Build orchestrator with Vapi/Retell or Pipecat.  
* Integrate STT (Deepgram/Google), LLM (Gemini Flash/GPT-4o-mini), TTS (OpenAI/Azure).  
* Tune turn-taking: silence threshold, interrupt sensitivity, semantic endpointing.  
* Build campaign flow (CSV upload, call scheduling, result storage).  
* Run a 100-call pilot with the college use case.  
* Measure: latency, transcription accuracy, extraction accuracy, user experience.

Phase 2 (4–6 weeks): Telugu pilot.

* Swap STT/TTS to Sarvam/Gnani.  
* Rewrite prompts and scripts in Telugu.  
* Test with native Telugu speakers (both Andhra and Telangana dialects).  
* Implement code-switching handling.  
* Decide whether to keep unified architecture or fork language pipelines.

Phase 3 (ongoing): Productionization.

* Add authentication/authorization to the dashboard.  
* Add DPDP compliance features (consent logs, data export, anonymization).  
* Scale concurrency, negotiate enterprise API quotas.  
* Build multi-campaign management, retry logic, reporting dashboard.

---

## **Summary of Where I Challenge Your Assumptions**

| Your assumption | My challenge |
| :---- | :---- |
| "Authentication not required initially" | Telephony KYC/DLT is mandatory regardless. Do not defer it. |
| "English architecture will transfer to Telugu" | It will not. Telugu needs separate STT/TTS vendors and tuning. Plan a separate pilot. |
| "Building everything ourselves gives better differentiation" | Your differentiation is conversation quality, not infrastructure. Use proven platforms for telephony and audio transport; invest in turn-taking and language quality. |
| "Need a large LLM for intelligence" | No. Small/fast models with deterministic validation are better for structured calls. |
| "Open-source TTS/STT is cheaper/better" | For Telugu, open-source is worse. Indian vendors (Sarvam/Gnani) are the realistic best. |
| "SIM/eSIM could work" | Not scalable, not appropriate for concurrent calling. |

---

Final note: My information reflects the world as of approximately May 2025\. Before you commit, verify current pricing, provider capabilities (especially Telugu STT/TTS quality and Indian DID availability), and Indian regulatory changes (TRAI AI voice disclosure rules may have evolved in 2026). The architecture and strategy above are designed to be robust to those changes—the key decisions (Indian CPaaS for telephony, managed orchestrator, pluggable STT/TTS/LLM, deterministic extraction layer) do not change if a specific vendor's pricing shifts.

# GPT approch

---

# **1\. Executive verdict**

### **Recommended architecture**

                   ADMIN WEB APP  
                         │  
                  CSV / Excel Upload  
                         │  
                         ▼  
                Campaign Orchestrator  
                         │  
                ┌────────┴────────┐  
                │                 │  
             Queue           Call State DB  
                │                 │  
                ▼                 │  
         Indian Telephony          │  
            Exotel                │  
                │                 │  
        PSTN / Mobile Network      │  
                │                 │  
                ▼                 │  
        WebSocket Audio Stream     │  
                │                 │  
                ▼                 │  
        ┌─────────────────────┐   │  
        │   Voice Runtime     │   │  
        │      Pipecat        │   │  
        └─────────┬───────────┘   │  
                  │  
        ┌─────────┼─────────┐  
        ▼         ▼         ▼  
       STT       LLM       TTS  
        │         │         │  
        │         │         │  
   Deepgram /  Fast LLM   Cartesia /  
   Sarvam      \+ tools    Sarvam  
        │         │         │  
        └─────────┼─────────┘  
                  │  
                  ▼  
            Audio Stream  
                  │  
                  ▼  
               Exotel  
                  │  
                  ▼  
               Person

### **My first-choice stack**

| Layer | Recommendation | Why |
| ----- | ----- | ----- |
| Indian telephony | **Exotel** | Strong India positioning \+ real-time bidirectional streaming |
| Voice runtime | **Pipecat** | Open, modular, provider-independent |
| STT English | **Deepgram Flux/Nova-3** | Excellent real-time voice-agent tooling |
| STT India/Telugu | **Sarvam Saaras** | Much stronger India-language positioning |
| TTS English | **Cartesia Sonic / ElevenLabs Flash** | Excellent real-time quality |
| TTS Telugu | **Sarvam Bulbul V3** | India/Telugu focus |
| LLM | **Fast model first**, large model selectively | Voice does not need maximum reasoning everywhere |
| Database | **PostgreSQL** | Call/campaign/state data is relational |
| Queue | **Redis \+ BullMQ** initially | Simple campaign scheduling/concurrency control |
| Backend | **Python/FastAPI** for voice runtime \+ Node/Next.js if preferred for dashboard | Python ecosystem fits Pipecat |
| Deployment | Docker \+ AWS/GCP/Azure/Indian-region infrastructure where appropriate | predictable scaling |
| Storage | S3-compatible object storage | recordings/transcripts |
| Observability | OpenTelemetry \+ structured call events | voice debugging requires timelines |

Exotel explicitly supports bidirectional WebSocket streaming for conversational bots, and its current documentation describes outbound calls, call status callbacks, recording, and direct WebSocket audio streaming.

Sarvam itself now documents an Exotel \+ Pipecat \+ Sarvam architecture for Indian-language voice agents, including Telugu, which is interesting because it validates the general architectural direction independently of our recommendation.

---

# **2\. First assumption I would challenge**

Your biggest potentially dangerous assumption is:

> "We need an Indian virtual number, therefore we should find an Indian equivalent of Twilio."

Not quite.

The **telephony provider is not the voice AI platform**.

You should deliberately separate:

Telephony  
    ↓  
Audio transport  
    ↓  
Voice orchestration  
    ↓  
STT  
    ↓  
LLM  
    ↓  
TTS

That separation is extremely important.

If you use a platform like Retell/Vapi for everything, you gain speed but lose control.

If you build everything yourself from raw SIP/RTP, you gain control but inherit a ridiculous amount of telecom engineering.

The sweet spot is:

> **Buy the telecom infrastructure. Build the intelligence layer.**

---

# **3\. Indian telephony landscape**

## **Tier 1: Exotel**

[Exotel](https://exotel.com/?utm_source=chatgpt.com)

### **Why I rank it \#1 for this project**

Exotel is unusually well aligned with what you need:

* Indian telephony  
* Indian numbers  
* outbound calls  
* call status  
* recording  
* WebSocket streaming  
* bidirectional audio  
* Voicebot integration  
* SIP  
* enterprise telecom infrastructure

Its Voicebot Applet supports two-way audio over WebSocket, specifically for conversational bots.

It also supports an API flow where your application initiates an outbound call, Exotel connects the call, and the AI bot receives audio through WebSocket.

### **Important technical detail**

Exotel's documented streaming format includes:

* 8 kHz mono PCM  
* WebSocket  
* JSON events  
* media chunks  
* DTMF  
* call start/stop events

It also supports higher sample rates through its streaming configuration.

That is exactly the type of interface we want.

### **Weakness**

Pricing isn't as transparently exposed as Plivo/Twilio.

You'll likely have to deal with:

* KYC  
* business documentation  
* account approval  
* commercial negotiation  
* concurrency/throughput discussions

For a serious production system, that's not necessarily bad.

For a random student wanting to call 500 people tomorrow, it is considerably less amusing.

---

# **4\. Plivo**

[Plivo](https://www.plivo.com/?utm_source=chatgpt.com)

Plivo is technically very interesting.

Current India pricing lists:

* outbound local calls: **₹0.60/min**  
* local number: **₹250/month**  
* browser/SIP: ₹0.34/min  
* local number requirements include **Certificate of Incorporation \+ GST**.

More importantly, Plivo supports:

* bidirectional WebSocket streaming  
* 8 kHz / 16 kHz PCM  
* μ-law  
* noise cancellation  
* status callbacks  
* audio playback back into the call  
* interruption/clear-audio events.

That's excellent for a voice runtime.

### **But**

The documentation's current India number requirements are a problem for a student prototype if you don't have an eligible business entity.

So:

**Technically:** excellent.

**For your India-first prototype:** probably \#2 behind Exotel.

---

# **5\. Twilio**

[Twilio](https://www.twilio.com/?utm_source=chatgpt.com)

Twilio remains one of the strongest programmable telecom platforms globally.

But India changes the equation.

Twilio's current India guidelines explicitly state that outbound calls to Indian PSTN numbers can only be made from **international, non-Indian numbers**.

That directly conflicts with one of your requirements:

> calls should appear legitimate/trustworthy with an Indian number.

Therefore:

### **Twilio is excellent globally.**

### **Twilio is not my recommended primary Indian PSTN layer for this project.**

Its India voice pricing currently lists approximately:

* $0.0496/min to Indian mobiles  
* $0.0699/min to Indian local numbers

and it doesn't offer Indian voice-enabled numbers in the same way you need.

So don't build the architecture around Twilio merely because every tutorial on the internet does.

---

# **6\. Knowlarity**

[Knowlarity](https://www.knowlarity.com/?utm_source=chatgpt.com)

Knowlarity is a serious Indian cloud-telephony player.

Current published pricing includes:

* ₹1,999/month inbound contact center  
* ₹2,999/month inbound \+ outbound contact center  
* ₹1,499 to ₹1,999/agent/month for WebRTC offerings  
* outbound pricing depending on product  
* automatic outbound dialer/OBD offerings.

### **Problem**

It is much more contact-center-oriented than developer-oriented.

For your project, I prefer a platform exposing clean real-time media primitives.

**Verdict:**

Good enterprise telephony option.

Not my first choice for building an experimental voice-AI runtime.

---

# **7\. Ozonetel**

[Ozonetel](https://ozonetel.com/?utm_source=chatgpt.com)

Worth considering for Indian production deployments.

It is especially relevant once you become:

* enterprise-facing  
* contact-center-heavy  
* campaign-heavy  
* compliance-heavy

ElevenLabs currently offers an Ozonetel integration specifically for real-time AI agents handling Indian inbound/outbound calls.

That is a useful signal that Ozonetel is viable for AI voice infrastructure.

But again, for your **developer-controlled prototype**, Exotel is cleaner.

---

# **8\. Indian telecom recommendation**

My ranking:

| Provider | India PSTN | Streaming | AI friendliness | Developer control | Recommendation |
| ----- | ----- | ----- | ----- | ----- | ----- |
| **Exotel** | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | **\#1** |
| **Plivo** | ★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | \#2 |
| **Ozonetel** | ★★★★★ | ★★★★ | ★★★★ | ★★★ | \#3 |
| **Knowlarity** | ★★★★★ | ★★★ | ★★★ | ★★★ | \#4 |
| **Twilio** | ★★ for your use case | ★★★★★ | ★★★★★ | ★★★★★ | Avoid as primary India PSTN |
| SIM/eSIM | ★★★ | ★ | ★ | ★ | Don't use |

---

# **9\. Why SIM/eSIM is the wrong architecture**

Don't build this around:

SIM card  
 ↓  
Android phone  
 ↓  
GSM audio  
 ↓  
AI

It sounds clever.

It is actually technical debt wearing a clever hat.

Problems:

* unreliable call control  
* difficult concurrency  
* limited automation  
* carrier restrictions  
* hardware dependency  
* poor observability  
* difficult scaling  
* difficult number management  
* difficult compliance  
* no clean media API

For one experimental call, fine.

For a platform, absolutely not.

---

# **10\. The telecom regulatory problem is bigger than you think**

This deserves special attention.

TRAI's current framework explicitly addresses **auto-dialer and robo-calls**.

The 2025 regulatory changes distinguish:

* promotional voice calls  
* service calls  
* transactional calls  
* auto-dialer/robocalls

and establish specific numbering approaches. TRAI's material says promotional auto-dialer/robocalls are associated with the **140 series**, while service/transactional voice calls are associated with **1600 or another allotted series**.

TRAI also defines a robocall as a call using artificial or prerecorded voice to interactively deliver a voice message without human involvement on the calling side.

This matters enormously.

Your college absence example is **not automatically equivalent to telemarketing**, but you cannot casually assume:

> "It's educational, therefore regulations don't apply."

The actual classification depends on:

* sender  
* purpose  
* recipient relationship  
* consent  
* communication category  
* provider implementation

And TRAI continues to update the framework. A 2026 consultation on further amendments was closed in April 2026\.

### **Even more important**

TRAI is now institutionalizing **AI/ML-based UCC detection** across operators.

So building something that behaves like:

10,000 calls  
\+  
random 10-digit caller ID  
\+  
automatic script  
\+  
no consent

is an excellent way to discover that telecom operators have opinions.

Very strong opinions.

---

# **11\. DLT and consent**

TRAI's current guidance says commercial communications operate through registered headers and distinguishes promotional from service communications.

Therefore, before production outbound campaigns, your architecture needs a **compliance layer**, not just a dialer.

I would create:

Campaign  
 ├── purpose  
 ├── communication\_type  
 ├── consent\_source  
 ├── consent\_timestamp  
 ├── recipient  
 ├── provider  
 ├── caller\_id  
 ├── script\_version  
 ├── recording\_policy  
 └── retention\_policy

This becomes extremely important later.

---

# **12\. Privacy and data protection**

Your system potentially stores:

* phone number  
* name  
* student ID  
* absence reason  
* recordings  
* transcripts  
* summaries  
* timestamps  
* potentially sensitive personal information

India's DPDP Rules were formally notified in November 2025, with phased commencement.

The government's published material describes the framework as operationalized with an 18-month phased compliance timeline.

Therefore, even during the prototype phase, architect for:

* encryption  
* deletion  
* retention periods  
* access controls  
* audit logs  
* consent records  
* data minimization

Don't build a database containing five years of voice recordings because "storage is cheap."

Cheap storage has a remarkable ability to become expensive evidence.

---

# **13\. Real-time voice architecture**

This is where your actual competitive advantage will come from.

A good system isn't:

STT → LLM → TTS

That's the kindergarten diagram.

A serious architecture is:

            TELEPHONY  
                 │  
                 ▼  
          AUDIO INGESTION  
                 │  
                 ▼  
          ┌─────────────┐  
          │ Audio Buffer│  
          └──────┬──────┘  
                 │  
          ┌──────▼──────┐  
          │     VAD     │  
          └──────┬──────┘  
                 │  
       ┌─────────▼─────────┐  
       │ Endpoint / Turn   │  
       │ Detection Engine  │  
       └─────────┬─────────┘  
                 │  
                 ▼  
                STT  
                 │  
                 ▼  
       Partial Transcript  
                 │  
                 ▼  
       Conversation State  
                 │  
          ┌──────▼──────┐  
          │ LLM / Policy│  
          └──────┬──────┘  
                 │  
         Streaming Tokens  
                 │  
                 ▼  
                TTS  
                 │  
           Audio Chunks  
                 │  
          ┌──────▼──────┐  
          │ Audio Queue │  
          └──────┬──────┘  
                 │  
          INTERRUPTION?  
           /           \\  
         YES            NO  
          │              │  
       CLEAR           PLAY  
       AUDIO

This is much closer to what you actually need.

---

# **14\. VAD is not endpoint detection**

This distinction is critical.

### **VAD**

Answers:

> "Is someone speaking?"

### **Endpoint detection**

Answers:

> "Has this person finished their turn?"

Those are not the same problem.

Example:

> "I was absent because... um... my..."

A naive VAD system may decide:

speech stopped  
→ respond

Human conversation does not.

The person is still thinking.

You need a turn detector that understands:

* silence duration  
* partial transcript  
* syntax  
* semantic incompleteness  
* speech prosody  
* conversation context

This is one reason Deepgram's current Flux model is interesting. It is specifically positioned for conversational speech recognition with turn detection and interruption handling.

---

# **15\. Barge-in**

This is probably the **single most visible quality feature**.

Suppose AI says:

> "So your expected return date is..."

User:

> "No, actually..."

The AI must stop.

Immediately.

Not:

> "So your expected return date is... No, actually..."

That is the classic AI phone-bot embarrassment.

Your pipeline should have:

Incoming audio  
      ↓  
VAD  
      ↓  
Barge-in detector  
      ↓  
CLEAR TTS BUFFER  
      ↓  
STOP PLAYBACK  
      ↓  
LISTEN

Plivo exposes explicit mechanisms for clearing buffered audio, and Exotel's voice-streaming architecture is designed for bidirectional conversational media.

---

# **16\. Latency targets**

Don't obsess over raw API latency.

Measure:

> **End of user's speech → first audible AI response**

That's the metric the human experiences.

I'd establish these internal targets:

| Metric | Target |
| ----- | ----- |
| Barge-in stop | \<150 ms |
| STT first partial | \<200 ms |
| End-of-turn detection | \~200–400 ms |
| LLM first token | \<200–400 ms |
| TTS first audio | \<200–300 ms |
| First audible response | **\~400–800 ms** |
| Excellent p95 | **\<1.2 s** |
| \>2 sec | Feels noticeably robotic |

These are engineering targets, not guarantees from vendors.

The biggest trick is **parallelism**.

Don't wait for:

complete STT  
→ complete LLM  
→ complete TTS

Instead:

partial STT  
    ↓  
LLM begins reasoning  
    ↓  
first useful phrase  
    ↓  
TTS begins  
    ↓  
audio starts  
---

# **17\. Streaming is not optional**

TTS should produce:

"Yes, I understand..."

before the complete answer exists.

Then:

"Yes, I understand... you were absent because..."

continues streaming.

ElevenLabs documents WebSocket TTS specifically for real-time text input and says its Flash models have roughly 75 ms model inference latency under representative conditions, while warning that real end-to-end latency will be higher.

Sarvam's Bulbul V3 currently advertises sub-250 ms first-byte streaming and 8 kHz telephony optimization.

---

# **18\. STT recommendation**

## **English**

### **\#1 Deepgram**

[Deepgram](https://deepgram.com/?utm_source=chatgpt.com)

Deepgram's current Flux model is explicitly aimed at conversational voice agents and includes turn detection/interruption handling. Nova-3 is positioned for noisy, multilingual and crosstalk-heavy audio.

Current published prices are roughly:

* Nova-3 monolingual: \~$0.0048/min  
* Nova-3 multilingual: \~$0.0058/min  
* Flux English: \~$0.0065/min  
* Flux multilingual: \~$0.0078/min.

That's extremely cheap relative to the overall voice stack.

### **\#2 Sarvam**

[Sarvam AI](https://www.sarvam.ai/?utm_source=chatgpt.com)

Sarvam is far more interesting once Indian languages enter the picture.

Current Saaras V3 supports 22 Indian languages \+ English and supports:

* real-time streaming  
* code mixing  
* Telugu  
* Indian English  
* word timestamps  
* speaker diarization.

Its published API pricing is ₹30/hour, or roughly **₹0.50/minute**.

### **My strategy**

Don't choose one STT permanently.

Build:

STTProvider  
    ├── DeepgramSTT  
    ├── SarvamSTT  
    └── GoogleSTT

Then benchmark them against **your actual calls**.

---

# **19\. TTS recommendation**

This is more nuanced.

## **English**

### **Cartesia**

[Cartesia](https://www.cartesia.ai/?utm_source=chatgpt.com)

Very strong candidate for low-latency English voice.

### **ElevenLabs**

[ElevenLabs](https://elevenlabs.io/?utm_source=chatgpt.com)

Still one of the strongest choices for expressive English.

Its Flash/Turbo API is currently priced around $0.05/1,000 characters, with multilingual models around $0.10/1,000 characters.

Its WebSocket streaming API is specifically designed for real-time generation.

---

# **20\. Telugu changes the equation**

This is where your roadmap is correct.

Don't assume:

Great English voice  
      ↓  
same model  
      ↓  
Great Telugu

That assumption is wrong.

Telugu needs:

* pronunciation  
* Telugu phonetics  
* regional variation  
* names  
* numbers  
* locations  
* code-switching  
* Tanglish  
* colloquial speech  
* speech rhythm

Sarvam is currently one of the most strategically interesting options here because Bulbul V3 explicitly supports Telugu and Indian-language voice generation, with code-switching and telephony optimization.

Sarvam's current documentation also lists Telugu as a supported STT language and supports mixed-language recognition.

### **Therefore:**

**English:**

Deepgram → fast LLM → Cartesia/ElevenLabs

**Telugu:**

Sarvam STT → fast LLM → Sarvam TTS

And the rest of the orchestration remains unchanged.

That's exactly why the provider abstraction matters.

---

# **21\. LLM strategy**

You do **not** need the largest reasoning model for every sentence.

A phone conversation has a very different computational profile from an agent doing software engineering.

Most turns are:

"Yes."  
"Okay."  
"I understand."  
"What date?"  
"Tuesday."  
"Can you repeat that?"

Using an enormous reasoning model for that is like hiring a constitutional lawyer to decide whether you want tea.

### **Use three layers**

                Voice Agent  
                     │  
          ┌──────────┼──────────┐  
          │          │          │  
      Deterministic  Fast LLM   Heavy LLM  
         Logic

### **Deterministic**

Use code for:

* call state  
* retries  
* validation  
* date parsing  
* phone numbers  
* campaign scheduling  
* termination conditions  
* structured extraction  
* compliance  
* tool permissions

### **Fast LLM**

Use for:

* normal conversation  
* paraphrasing  
* intent recognition  
* contextual responses  
* natural follow-ups

### **Strong LLM**

Use only when needed:

* ambiguous reasoning  
* complicated user requests  
* knowledge-intensive tasks  
* difficult tool planning

---

# **22\. Native speech-to-speech vs cascaded pipeline**

This is an important decision.

There are two architectures.

### **Cascaded**

Audio  
 ↓  
STT  
 ↓  
LLM  
 ↓  
TTS  
 ↓  
Audio

### **Native realtime model**

Audio  
 ↓  
Realtime multimodal model  
 ↓  
Audio

Google's Gemini Live API currently supports bidirectional real-time audio with native audio output over WebSockets.

Google's current Gemini pricing also exposes native-audio realtime models.

OpenAI also has a Realtime API for real-time audio interaction.

### **Native speech-to-speech advantage**

Potentially:

* lower latency  
* more natural turn-taking  
* better prosody  
* less pipeline overhead

### **Cascaded advantage**

You can independently control:

* STT  
* turn detection  
* LLM  
* TTS  
* transcript  
* structured extraction  
* language  
* provider  
* debugging

### **For your project**

I choose **cascaded first**.

Why?

Because your project isn't merely:

> "Make a cool voice demo."

It's:

> "Build an AI calling platform."

You need observability.

---

# **23\. Pipecat is the right abstraction**

[Pipecat](https://github.com/pipecat-ai/pipecat?utm_source=chatgpt.com)

Pipecat already supports real-time voice pipelines and WebSocket telephony transports.

Its architecture allows:

Telephony  
    ↓  
Transport  
    ↓  
VAD  
    ↓  
STT  
    ↓  
LLM  
    ↓  
TTS

with interchangeable providers.

Its current quickstart uses:

* Deepgram  
* OpenAI  
* Cartesia

and reports sub-second full-round-trip behavior in its sample architecture.

More importantly, Sarvam has an existing Pipecat integration and Exotel example.

That combination is unusually attractive for your India → Telugu roadmap.

---

# **24\. Why I don't recommend Vapi as the core**

[Vapi](https://vapi.ai/?utm_source=chatgpt.com)

Vapi is genuinely useful.

Current pricing is approximately:

**$0.05/minute platform fee**

plus provider costs passed through at cost.

That's attractive.

But you're trying to learn/build the underlying architecture.

Vapi gives you:

telephony  
\+  
STT  
\+  
LLM  
\+  
TTS  
\+  
orchestration

conveniently.

The downside is that your actual differentiator becomes:

> "We configured Vapi well."

That's not enough for the serious platform you're describing.

### **Use Vapi for:**

* rapid experiments  
* benchmarking  
* reference implementation  
* proving product-market fit

### **Don't make it your architectural foundation.**

---

# **25\. Retell is stronger, but same strategic problem**

[Retell AI](https://www.retellai.com/?utm_source=chatgpt.com)

Retell is probably one of the best turnkey choices for high-quality voice agents.

Current pricing is approximately:

**$0.07–$0.31/minute**

depending on configuration. It includes a voice runtime, analytics, APIs, simulation, and 20 concurrent calls on the pay-as-you-go plan.

It supports a wide range of models and voices, including GPT, Claude, Gemini, Cartesia and ElevenLabs.

### **This is actually a very good product.**

But:

**You are trying to build the underlying product.**

So I'd use Retell as a **benchmark**.

Build the same conversation on:

Retell  
vs  
your Pipecat stack

Then measure:

* response latency  
* barge-in  
* WER  
* completion rate  
* human rating  
* cost

If your system can't beat it, you learn exactly where you're weak.

That's far more useful than blindly choosing one.

---

# **26\. Competitive landscape**

The serious ecosystem currently includes:

### **Infrastructure/platform**

* [Exotel](https://exotel.com/?utm_source=chatgpt.com)  
* [Plivo](https://www.plivo.com/?utm_source=chatgpt.com)  
* [Twilio](https://www.twilio.com/?utm_source=chatgpt.com)  
* [Ozonetel](https://ozonetel.com/?utm_source=chatgpt.com)  
* [Knowlarity](https://www.knowlarity.com/?utm_source=chatgpt.com)

### **Voice AI platforms**

* [Retell AI](https://www.retellai.com/?utm_source=chatgpt.com)  
* [Vapi](https://vapi.ai/?utm_source=chatgpt.com)  
* [ElevenLabs](https://elevenlabs.io/?utm_source=chatgpt.com)  
* [LiveKit](https://livekit.io/?utm_source=chatgpt.com)  
* [Pipecat](https://github.com/pipecat-ai/pipecat?utm_source=chatgpt.com)

### **India-focused AI**

* [Sarvam AI](https://www.sarvam.ai/?utm_source=chatgpt.com)  
* Haptik  
* Yellow.ai  
* Skit.ai  
* Kore.ai  
* Ozonetel

The strongest Indian enterprise players increasingly differentiate on **telephony reliability, compliance, multilingual support, and concurrency**, not merely the LLM. This is also reflected in current Indian enterprise voice-AI positioning from Exotel and Haptik.

---

# **27\. Cost model**

Let's use a realistic prototype assumption:

### **Average call**

**5 minutes**

Then:

| Calls | Minutes |
| ----- | ----- |
| 100 | 500 |
| 1,000 | 5,000 |
| 10,000 | 50,000 |
| 100,000 | 500,000 |

Now approximate the AI layer.

### **STT**

Sarvam:

₹30/hour

≈ **₹0.50/minute**.

Deepgram is dramatically cheaper on published raw STT pricing, but the correct choice depends on accuracy and Indian-language performance.

### **TTS**

Sarvam Bulbul V3:

₹30/10,000 characters.

A five-minute conversation might produce around 600–1,000 assistant words depending on speaking behavior, so TTS cost can remain relatively low.

### **LLM**

For a normal short phone conversation, the LLM is unlikely to dominate cost if you use an efficient model and aggressively manage context.

### **Infrastructure**

At prototype scale:

Probably negligible compared with telecom \+ AI usage.

At 100k concurrent-scale minutes, infrastructure and observability become real costs.

---

# **28\. Practical prototype cost estimate**

For an India-first cascaded system, I would initially budget approximately:

### **₹1.5–₹3.5 per connected minute**

for the AI \+ telecom stack, depending heavily on:

* telephony provider  
* STT  
* TTS  
* LLM  
* call duration  
* recording  
* infrastructure

This is an **engineering estimate**, not a vendor quote.

At 5-minute average calls:

| Calls/month | Minutes | Approx operating cost |
| ----- | ----- | ----- |
| 100 | 500 | ₹750–₹1,750 |
| 1,000 | 5,000 | ₹7,500–₹17,500 |
| 10,000 | 50,000 | ₹75k–₹1.75L |
| 100,000 | 500,000 | ₹7.5L–₹17.5L |

Then optimize.

The raw numbers will change substantially once you negotiate Indian telecom pricing and choose exact model combinations.

---

# **29\. Why your average call duration matters enormously**

If you allow an AI agent to talk forever:

"Okay..."  
"Right..."  
"Yes..."  
"So..."  
"Let me understand..."

you burn money.

Your agent should have:

* objective  
* state  
* maximum duration  
* maximum turns  
* completion criteria  
* early termination  
* voicemail detection  
* silence timeout

For the absence example:

1\. Identify student  
2\. Confirm identity  
3\. Ask absence reason  
4\. Ask expected return  
5\. Ask whether support is required  
6\. Confirm  
7\. End

That's it.

Don't let the model discover philosophy halfway through the call.

---

# **30\. Campaign architecture**

The campaign system should not directly call people from the web request.

Use a queue.

Admin  
 │  
 ▼  
Campaign  
 │  
 ▼  
Contacts  
 │  
 ▼  
Redis Queue  
 │  
 ├── Worker 1  
 ├── Worker 2  
 ├── Worker 3  
 ├── Worker 4  
 └── Worker N

Each worker:

reserve contact  
      ↓  
check compliance  
      ↓  
initiate call  
      ↓  
track call SID  
      ↓  
start voice session  
      ↓  
store events  
      ↓  
finalize result  
---

# **31\. Call state machine**

Don't let the LLM own call state.

Use deterministic state.

CREATED  
   ↓  
QUEUED  
   ↓  
DIALING  
   ↓  
RINGING  
   ↓  
ANSWERED  
   ↓  
AI\_ACTIVE  
   ├── HUMAN\_TRANSFER  
   ├── COMPLETED  
   ├── USER\_HANGUP  
   ├── AI\_HANGUP  
   ├── TIMEOUT  
   └── ERROR

DIALING  
   ├── BUSY  
   ├── NO\_ANSWER  
   └── FAILED

This gives you reliable reporting.

---

# **32\. Structured extraction**

Never depend on the final LLM summary to reconstruct everything.

Maintain structured state during the conversation.

Example:

{  
  "student\_id": "STU1024",  
  "answered": true,  
  "absence\_reason": "fever",  
  "expected\_return\_date": "2026-08-15",  
  "needs\_support": false,  
  "confidence": 0.91,  
  "call\_duration\_seconds": 182  
}

The LLM can propose values.

Your application validates them.

For example:

LLM says:  
"return date \= next Friday"

        ↓

deterministic date resolver

        ↓

2026-08-21

This is far safer.

---

# **33\. Don't let the LLM control everything**

The architecture should be:

LLM \= intelligence  
Code \= authority

The LLM can say:

> "The student says they will return Monday."

Your code determines:

* what Monday means  
* whether it is a valid date  
* whether it falls within allowed range  
* whether the field is complete

This principle becomes increasingly important in high-stakes voice systems.

Recent research into voice agents for Indian populations is also moving toward combining LLMs with deterministic validation and flow control rather than allowing the model to control the entire process.

---

# **34\. Concurrency**

Your system should have two separate concurrency limits.

### **Telephony concurrency**

How many calls can Exotel place?

### **AI concurrency**

How many voice sessions can your infrastructure process?

They are not the same.

At:

### **1 call**

Nothing interesting happens.

### **10 calls**

You discover bugs.

### **100 calls**

You discover architecture.

### **1,000 calls**

You discover telecom.

At 1,000 concurrent calls, you need:

* multiple workers  
* connection pools  
* queue partitioning  
* autoscaling  
* provider CPS management  
* Redis  
* backpressure  
* WebSocket lifecycle management  
* CPU/memory monitoring  
* model rate-limit management  
* provider failover

---

# **35\. Don't scale the LLM blindly**

Imagine:

1,000 calls  
×  
one LLM request every 5 seconds

You suddenly have massive request throughput.

Instead:

1000 sessions  
     │  
     ▼  
fast model  
     │  
     ├── most requests  
     │  
     └── heavy model only when necessary

This dramatically reduces cost and rate-limit pressure.

---

# **36\. Database**

Use PostgreSQL.

Not MongoDB for this core data.

Your entities naturally look like:

organizations  
campaigns  
contacts  
calls  
call\_events  
conversation\_turns  
transcripts  
extractions  
recordings  
providers  
agents  
agent\_versions

Example:

campaign  
   │  
   ├── contacts  
   │       │  
   │       └── calls  
   │              │  
   │              ├── events  
   │              ├── transcript  
   │              ├── extraction  
   │              └── recording

This is relational data.

Postgres wins.

---

# **37\. Frontend**

Your initial dashboard can be:

Next.js  
\+  
TypeScript  
\+  
Tailwind  
\+  
PostgreSQL

Pages:

/dashboard

/campaigns  
/campaigns/:id

/campaigns/:id/contacts

/calls/:id

/analytics

/settings

Campaign page:

Campaign: Student Absence

Total:       1,000  
Answered:      721  
No Answer:     183  
Busy:           61  
Failed:         35

Avg duration: 2m 41s

Completion: 78.4%

Then export:

CSV  
XLSX  
JSON  
---

# **38\. The voice session object**

Every active call needs an isolated session.

VoiceSession(  
    call\_id,  
    campaign\_id,  
    contact\_id,  
    language,  
    state,  
    conversation\_history,  
    extracted\_fields,  
    audio\_buffers,  
    provider\_metadata  
)

Never put active call state into global process memory.

Because:

Call A  
Call B  
Call C

must never accidentally share:

"Okay, your fever..."

with another person.

That would be a spectacularly bad demo.

---

# **39\. English → Telugu migration**

The beautiful part is that most of your system doesn't change.

### **Doesn't change**

Campaign engine  
Call state  
Database  
Dashboard  
Queue  
Telephony  
Analytics  
Structured extraction  
Tool system  
Observability

### **Changes**

STT  
TTS  
Language detection  
Prompting  
Pronunciation  
Evaluation dataset  
Turn-taking tuning  
Normalization  
Names  
Numbers

So your architecture should have:

LanguageProfile(  
    language="en-IN",  
    stt\_provider="deepgram",  
    tts\_provider="cartesia",  
    normalization="english"  
)

and:

LanguageProfile(  
    language="te-IN",  
    stt\_provider="sarvam",  
    tts\_provider="sarvam",  
    normalization="telugu"  
)

Same agent.

Different speech stack.

---

# **40\. Telugu should be tested separately**

Build a Telugu evaluation dataset.

Not:

> "It sounds good to me."

That's worthless.

Create \~500–2,000 representative utterances:

"నాకు జ్వరం వచ్చింది"

"నిన్న కాలేజీకి రాలేకపోయాను"

"రేపు వస్తాను"

"నాకు ఖచ్చితంగా తెలియదు"

"అది సోమవారం అనుకుంటా"

"ఫోన్ సరిగ్గా వినిపించడం లేదు"

Then add:

### **Code-switching**

"నాకు fever ఉంది"

### **Tanglish**

"Naku fever vachindi"

### **Names**

"నా పేరు శ్రీనివాస్"

### **Numbers**

"రెండు రోజులు"  
"twenty second"  
"22nd"

### **Regional variation**

Telangana Telugu ≠ Andhra Telugu ≠ formal Telugu.

That's where your eventual moat could actually emerge.

---

# **41\. Your real competitive advantage**

It will **not** be:

> "We use GPT."

Everyone uses GPT.

It will not be:

> "We use AI."

Congratulations, the year is 2026\.

Your moat could become:

Indian telephony  
\+  
low-latency orchestration  
\+  
excellent interruption handling  
\+  
Indian accent STT  
\+  
Telugu conversational data  
\+  
structured workflows  
\+  
reliability  
\+  
evaluation infrastructure

Especially:

### **Your evaluation dataset.**

If you collect thousands of real-world anonymized conversational examples and systematically measure:

* WER  
* latency  
* interruption success  
* turn errors  
* hallucination rate  
* extraction accuracy  
* task completion  
* human naturalness rating

you start developing something genuinely difficult to copy.

---

# **42\. Voice quality benchmark**

Build a score out of 100\.

### **Naturalness: 20**

Does it sound human?

### **Latency: 20**

Does it respond quickly?

### **Turn-taking: 15**

Does it know when to speak?

### **Barge-in: 15**

Does it stop immediately?

### **STT accuracy: 10**

Does it understand correctly?

### **Task completion: 10**

Did it accomplish the goal?

### **Extraction accuracy: 5**

Did it record structured data correctly?

### **Recovery: 5**

Can it recover from misunderstandings?

Then:

Human baseline  
Retell  
Vapi  
Your system

Run the same conversations.

Now you're engineering instead of vibes-based benchmarking.

---

# **43\. Biggest project risks**

Here is where I'd be most worried.

## **Risk \#1: Robotic turn-taking**

**Probability: very high**

Most voice agents fail here before they fail at intelligence.

---

## **Risk \#2: Latency**

**Probability: high**

A brilliant model with 2-second response latency feels stupid.

---

## **Risk \#3: Telecom restrictions**

**Probability: high**

Especially outbound campaigns.

---

## **Risk \#4: Number provisioning**

**Probability: medium-high**

A student prototype may not have all documentation required for production numbers.

---

## **Risk \#5: Telugu quality**

**Probability: high**

English performance tells you almost nothing about Telugu conversational quality.

---

## **Risk \#6: Provider lock-in**

**Probability: very high**

If your business logic is embedded inside Retell/Vapi/etc., migration becomes painful.

---

## **Risk \#7: LLM hallucinations**

**Probability: high**

Especially when the agent is asked something outside its allowed scope.

---

## **Risk \#8: Bad extraction**

**Probability: medium**

The conversation may sound perfect while the database gets the wrong date.

That's worse than an obvious failure because it silently corrupts your results.

---

## **Risk \#9: Cost explosion**

**Probability: medium**

Especially if calls become long and model selection is careless.

---

# **44\. My final provider strategy**

## **Telephony**

### **Primary**

**Exotel**

### **Secondary**

**Plivo**

### **Enterprise alternative**

**Ozonetel**

### **Benchmark/global**

**Twilio**

---

# **45\. STT**

### **English**

**Deepgram Flux / Nova-3**

### **Indian English / Telugu**

**Sarvam Saaras**

### **Backup**

Google Speech / another provider

Don't hard-code one vendor.

---

# **46\. TTS**

### **English**

Test:

1. Cartesia  
2. ElevenLabs Flash  
3. OpenAI  
4. Google

### **Telugu**

Start with:

**Sarvam Bulbul V3**

Sarvam currently advertises 35+ voices across 11 Indian languages, including Telugu, with streaming and telephony-oriented output.

---

# **47\. LLM**

### **Default**

Fast model.

### **Heavy reasoning**

Only when required.

### **Architecture**

LLM interface  
    │  
    ├── OpenAI  
    ├── Gemini  
    ├── Anthropic  
    └── local model

Don't let the LLM provider become your platform.

---

# **48\. Voice orchestration**

### **Pipecat**

This is my strongest architectural recommendation.

Not because it is trendy.

Because it gives you the thing you actually need:

> control over the pipeline without having to implement the entire media-processing stack from scratch.

Pipecat explicitly supports WebSocket telephony transports and provider components.

---

# **49\. Alternative architecture**

There is another viable route:

Exotel  
   ↓  
ElevenLabs Agents  
   ↓  
LLM \+ TTS \+ STT \+ orchestration

ElevenLabs now has direct Exotel integration using WebSocket and positions it specifically for Indian contact centers.

This could give you a much faster proof of concept.

### **But I would use it as:**

**Benchmark / rapid MVP**

rather than:

**core architecture**

because you want control over the speech stack and Telugu migration.

---

# **50\. Recommended development roadmap**

## **Phase 0: Telephony proof**

**1–3 days**

Goal:

Browser/API  
 ↓  
Exotel  
 ↓  
Indian phone

Verify:

* number  
* KYC  
* outbound call  
* caller ID  
* call status  
* WebSocket  
* audio

Do not touch AI yet.

---

## **Phase 1: Audio pipeline**

**3–5 days**

Build:

Exotel  
 ↓  
WebSocket  
 ↓  
Pipecat  
 ↓  
VAD  
 ↓  
STT  
 ↓  
TTS  
 ↓  
Exotel

Goal:

> caller speaks → AI repeats/answers

---

## **Phase 2: Real conversation**

**5–10 days**

Add:

* LLM  
* streaming  
* context  
* interruption  
* endpoint detection  
* silence handling

---

## **Phase 3: Structured workflow**

**3–7 days**

Add:

Campaign  
 ↓  
Contact  
 ↓  
Call  
 ↓  
Extraction  
 ↓  
Result  
---

## **Phase 4: Dashboard**

**5–10 days**

Build:

* upload  
* contact preview  
* campaign start  
* live status  
* results  
* transcript  
* summary  
* export

---

## **Phase 5: Evaluation**

**1–2 weeks**

Create:

* latency benchmarks  
* WER benchmarks  
* interruption tests  
* extraction tests  
* human rating  
* failure dataset

This phase is more important than adding another 15 features.

---

## **Phase 6: Telugu**

Only after English is genuinely good.

Then:

Sarvam STT  
\+  
Sarvam TTS  
\+  
same runtime

Add:

* Telugu  
* Tanglish  
* code-switching  
* pronunciation dictionary  
* regional dialect tests

Sarvam's current speech stack already exposes Telugu, code-mixing, streaming and pronunciation-related capabilities, making it a strong candidate for this phase.

---

# **51\. The architecture I would actually build**

                   ┌──────────────────────┐  
                    │       Next.js        │  
                    │     Admin Dashboard  │  
                    └──────────┬───────────┘  
                               │  
                         REST / WebSocket  
                               │  
                    ┌──────────▼───────────┐  
                    │      FastAPI         │  
                    │   Control Plane      │  
                    └──────────┬───────────┘  
                               │  
             ┌─────────────────┼─────────────────┐  
             │                 │                 │  
             ▼                 ▼                 ▼  
         PostgreSQL          Redis            Object Store  
             │                 │                 │  
             │                 ▼                 │  
             │          Campaign Workers         │  
             │                 │                 │  
             │                 ▼                 │  
             │              Exotel               │  
             │                 │                 │  
             │          PSTN / Mobile            │  
             │                 │                 │  
             │                 ▼                 │  
             │         WebSocket Audio           │  
             │                 │                 │  
             │          ┌──────▼──────┐          │  
             │          │   Pipecat   │          │  
             │          │ Voice Engine│          │  
             │          └──────┬──────┘          │  
             │                 │                 │  
             │       ┌─────────┼─────────┐       │  
             │       ▼         ▼         ▼       │  
             │     Deepgram   LLM      Sarvam    │  
             │       │         │         │       │  
             │       └─────────┼─────────┘       │  
             │                 │                 │  
             │                 ▼                 │  
             │               TTS                 │  
             │                 │                 │  
             └─────────────────┼─────────────────┘  
                               │  
                               ▼  
                         Call Result  
---

# **52\. One important change to your original plan**

You described the system as domain-independent from the beginning.

I would **not** do that.

Build the runtime generically.

But build the **first agent around one narrow workflow**.

For example:

College absence verification

Why?

Because voice quality is difficult enough.

You don't need:

absence  
sales  
customer support  
appointments  
collections  
surveys  
lead qualification

simultaneously.

The platform should be generic.

The first agent should not be.

---

# **53\. The first MVP should therefore be**

### **"AI Student Absence Calling Agent"**

Input:

student\_id,name,phone  
ST001,Rahul,+91...  
ST002,Priya,+91...

Agent:

Hello Rahul, this is an automated call from XYZ College.

We noticed that you were absent today.

Could you tell me the reason?

Then:

Reason?  
Expected return?  
Need assistance?

Then:

Thank you. We have recorded that information.  
Have a good day.

Output:

student\_id  
name  
phone  
call\_status  
absence\_reason  
expected\_return  
support\_required  
duration  
confidence  
transcript  
summary

That gives you a complete vertical slice of the entire platform.

---

# **54\. Final stack decision**

If we were starting development **today**, my stack would be:

Frontend  
Next.js \+ TypeScript \+ Tailwind

Control API  
FastAPI

Voice Runtime  
Pipecat

Telephony  
Exotel

Queue  
Redis \+ BullMQ / Celery

Database  
PostgreSQL

Storage  
S3-compatible

English STT  
Deepgram Flux

English TTS  
Cartesia / ElevenLabs Flash

Indian/Telugu STT  
Sarvam Saaras

Telugu TTS  
Sarvam Bulbul V3

LLM  
Fast GPT/Gemini model  
\+  
strong model fallback

Observability  
OpenTelemetry

Deployment  
Docker  
\+  
AWS/GCP/Azure

CI/CD  
GitHub Actions

The most important architectural rule:

> **No provider-specific business logic inside the agent.**

Instead:

VoiceRuntime  
    ↓  
Provider Interfaces  
    ├── TelephonyProvider  
    ├── STTProvider  
    ├── TTSProvider  
    ├── LLMProvider  
    └── StorageProvider

That one decision will save you enormous pain when you move from English to Telugu.

---

# **55\. Bottom line**

Your original instinct to prioritize **conversation quality over simply making calls** is correct. The architecture should therefore optimize the things humans actually notice: response latency, turn-taking, barge-in, speech recognition, pacing and recovery.

But I would change the implementation philosophy:

### **Don't build:**

> "A Vapi/Retell clone."

### **Build:**

> **An India-first voice runtime that happens to use Exotel for telecom.**

The strongest initial combination is:

**Exotel \+ Pipecat \+ Deepgram \+ fast LLM \+ Cartesia/ElevenLabs**

and then:

**Exotel \+ Pipecat \+ Sarvam Saaras \+ fast LLM \+ Sarvam Bulbul V3**

for Telugu.

The biggest technical moat is not the LLM. It is the **real-time orchestration \+ evaluation \+ Indian-language speech quality \+ telecom reliability**.

And the biggest non-technical risk is not model quality. It is **Indian outbound-call compliance and number provisioning**. TRAI's current framework explicitly regulates auto-dialer/robocall behavior, commercial communication categories and numbering, while its 2026 work is increasing automated UCC detection.

So I would **not start by building the dashboard**.

I would start with the hardest proof:

Exotel Indian number  
        ↓  
real mobile call  
        ↓  
bidirectional audio  
        ↓  
Pipecat  
        ↓  
VAD \+ turn detection  
        ↓  
STT  
        ↓  
fast LLM  
        ↓  
streaming TTS  
        ↓  
barge-in  
        ↓  
human-quality conversation

If that loop feels genuinely good, everything else is engineering.

If that loop feels robotic, the dashboard is just a beautifully designed way to display failure.

# gemini 3.6 flash

## Critical Assumption Audit & Technical Reality Check

Before building a voice AI platform for the Indian telecommunications landscape, we must address three flawed architectural assumptions commonly held by engineering teams:

### Assumption 1: SIM Cards or Mobile GSM Gateways Can Scale Outbound AI Calling

* The Flaw: Utilizing physical SIM cards, eSIMs, or local GSM gateways (such as GoIP boxes) to route AI calls is unsuitable for production systems.  
*   
* The Reality: Commercial SIMs operate under strict Indian TRAI/DoT Fair Usage Policies (FUP). Automated calling over regular consumer SIMs triggers instant network-level fraud detection, leading to IMEI/SIM blocking and phone number blacklisting. Furthermore, local SIM gateways offer zero native WebSockets, poor audio quality (lacking direct digital PCM capture), and no scalable concurrency. You must use enterprise-grade Cloud Telephony or Programmable SIP Trunking.  
* 

### Assumption 2: An English Voice-AI Pipeline Can Effortlessly Adapt to Indian Languages

* The Flaw: Assuming that swapping an English STT/TTS engine with a Telugu STT/TTS engine on an existing pipeline will retain fluid, low-latency conversation quality.  
*   
* The Reality: Standard global models (OpenAI, Deepgram, ElevenLabs) degrade significantly on Indian telephonic audio (8kHz bandpass filtered), Indian proper nouns, regional dialects, and code-switching (Tanglish / Telugu-English). Indic languages require specific acoustic modeling, custom VAD tuning for longer conversational pauses, higher token density handling in LLMs, and localized TTS engines (e.g., Sarvam AI).  
* 

### Assumption 3: Turn-Based AI Architecture ("Listen $\\rightarrow$ Process $\\rightarrow$ Speak") can feel Human

* The Flaw: Relying on standard sequential API calls where the system waits for audio to complete before processing.  
*   
* The Reality: Human phone conversations operate on continuous, full-duplex feedback. A user says "uh-huh" or pauses to think. Sequential pipelines cause high perceived latency ($\>1.5\\text{s}$) or aggressive, unnatural interruptions. Achieving human conversation requires a full-duplex, streaming-first pipeline using bidirectional WebSockets or WebRTC/SIP, continuous energy/semantic VAD, and real-time audio frame manipulation.  
* 

## 1\. Telephony & Indian Telecom Options

To make legitimate outbound calls in India with proper Caller ID, low latency, and continuous real-time audio access, your system architecture must integrate directly with Indian Telecom Service Providers (TSPs) or compliant international CPaaS platforms.

### Architecture Options Comparison

| Option | Inbound/Outbound Audio Path | Indian CLI Support | Regulatory Compliance | Concurrency Capabilities | Real-Time Audio Streaming |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Indian Cloud Telephony (Exotel, Tata Tele, MyOperator) | HTTP Webhooks / WebSockets | High (Fixed Local / 140 / 160 Series) | High (Full TRAI/DLT Compliance) | High (Scalable via virtual channels) | Excellent (Exotel Voicebot Applet / Audio Streaming over WSS) |
| Global CPaaS with India POP (Plivo, Twilio India) | SIP Trunking / Bidirectional WSS | High (Must complete Indian Entity KYC) | High (Enforces TRAI DLT scrubbing) | Unlimited (Elastic SIP / Channel scaling) | Excellent (Direct WSS / Native LiveKit & Pipecat adapters) |
| Direct SIP Trunking (Tata Comms, Airtel Enterprise) | Pure SIP/RTP Protocol | Enterprise Direct CLI | Enterprise Legal Agreement Required | Very High (Dedicated Bandwidth E1/PRI/IP-SIP) | Raw RTP Audio (Requires custom SBC/RTP Media Gateway) |
| GSM Gateways / SIM Boxes | Analog/GSM to SIP | Single Mobile Number | Illegal / High Risk (Banned by TRAI for commercial transit) | Very Low (Limited by hardware ports & SIM locks) | Poor (A/D conversion distortion, high jitter) |

### Regulatory, KYC, and DLT Requirements in India

1. DLT (Distributed Ledger Technology) Registration: Every business placing commercial or automated voice calls in India must register as a Principal Entity on a telecom DLT portal (Jio, Airtel, Vodafone Idea, or Tata).  
2.   
3. 140 vs. 160 Number Series (TRAI Regulations):  
4. 

   * 140 Series: Mandatory prefix (+91-140-XXXXXXX) for Promotional/Telemarketing calls. Bypasses non-DND (Do Not Disturb) numbers only; blocked on DND numbers.  
   *   
   * 160 Series: Designated prefix (+91-160-XXXXXXX or 1600\) reserved exclusively for Service and Transactional calls (e.g., student attendance alerts, BFSI reminders, OTPs). Calls can reach DND-registered numbers provided explicit prior consent exists.  
   *   
5. KYC Documents Required for Provisioning: Certificate of Incorporation, GST Registration, Company PAN, Authorized Signatory LOA (Letter of Authorization), and proof of physical office in India.  
6. 

### Telecom Recommendation for Prototype vs. Production

* For Prototype: Use Plivo or Exotel. Both offer compliant Indian virtual numbers with direct Bidirectional WebSocket Audio Streaming (PCM 8kHz mono, Slinc/Base64). This bypasses the complexity of building custom Session Border Controllers (SBC) while keeping latency low ($\<100\\text{ms}$ telephonic transport).  
*   
* For High-Scale Production: Transition to Direct Enterprise Cloud SIP Trunking (Plivo / Tata Communications) connected directly to a self-hosted media server cluster (LiveKit SIP ingress/egress).  
* 

## 2\. Real-Time Voice Pipeline Architecture

To achieve a natural human-like voice conversation, you must avoid coarse turn-taking. The diagram below illustrates the continuous, event-driven streaming pipeline:

                         FULL-DUPLEX REAL-TIME AUDIO PIPELINE  
                            
Caller Phone  \<---\> Telephony Provider \<---\> WebSocket Bridge (PCM 8kHz Audio Streams)  
                        (Plivo / Exotel)               |  
                                                      v  
  \+-----------------------------------------------------------------------------------+  
  |                              AGENT ORCHESTRATION ENGINE                            |  
  |                                                                                   |  
  |  \+---------------------+      \+---------------------+      \+-------------------+  |  
  |  |  VAD & Endpointing  | \---\> |   Streaming STT     | \---\> | Dialogue Manager  |  |  
  |  | (Silero / TenSOFM)  |      |  (Deepgram / Sarvam)|      | & Tool Execution  |  |  
  |  \+---------------------+      \+---------------------+      \+-------------------+  |  
  |             |                                                        |            |  
  |             v Interrupt Event (Barge-In)                             v Text Stream|  
  |  \+--------------------------------------------------+      \+-------------------+  |  
  |  |      Audio Frame Buffer & Output Controller      | \<--- |   Streaming TTS   |  |  
  |  |      (Clears queue instantly upon barge-in)       |      |(Cartesia / Sarvam)|  |  
  |  \+--------------------------------------------------+      \+-------------------+  |  
  \+-----------------------------------------------------------------------------------+

### Key Architectural Components

1. Telephony Bridge & Audio Transcoder: Converts telephony audio streams (G.711 $\\mu$-law/A-law, 8kHz PCM) into standard WebSockets PCM chunks (typically 20ms–100ms frames).  
2.   
3. Dual-Layer Voice Activity Detection (VAD):  
4. 

   * Local Energy/Acoustic VAD: High-speed (e.g., Silero VAD, running in $\<10\\text{ms}$) running directly on incoming audio frames to detect instant vocal onset or interruption.  
   *   
   * Semantic/LLM VAD: Secondary analysis to determine if the user has reached a pause (thinking) versus a completed utterance (turn boundary).  
   *   
5. Streaming Speech-to-Text (STT): Maintains an open WebSocket connection, converting incoming chunks into interim transcriptions with sub-word timestamps and final transcriptions.  
6.   
7. Conversation Orchestration State Machine: Manages state transitions, session variables (student data, call status), tool execution, and prompt injection.  
8.   
9. Ultra-Low TTFT (Time-To-First-Token) LLM: Receives text context and streams output tokens immediately.  
10.   
11. Streaming Text-to-Speech (TTS): Processes token chunks, generates audio bytes (24kHz or 16kHz), and downsamples them to telephonic 8kHz PCM.  
12.   
13. Interruption-Aware Audio Playback Buffer: Holds audio frames being sent back over the WebSocket. If the VAD flags a barge-in event, it fires a clear\_buffer signal to instantly purge unplayed audio.  
14. 

## 3\. Latency Budget & Optimization Strategies

Human speech turn-taking typically occurs within a 200ms to 500ms window. In telephonic voice AI, a total round-trip response time exceeding 800ms creates an unnatural "walkie-talkie" cadence.

### System Latency Budget

$$\\text{Latency}\_{\\text{Total}} \= T\_{\\text{VAD}} \+ T\_{\\text{STT}} \+ T\_{\\text{LLM\\\_TTFT}} \+ T\_{\\text{TTS\\\_TTFB}} \+ T\_{\\text{Network\\\_Jitter}}$$

| Component | Target Latency (Optimal) | Realistic Latency (Standard Setup) | Optimization Strategy |
| :---- | :---- | :---- | :---- |
| VAD / Silence Detection | $100\\text{ms} \- 200\\text{ms}$ | $500\\text{ms}$ | Use sub-frame acoustic VAD \+ speculative execution instead of waiting for long trailing silence. |
| Streaming STT | $100\\text{ms} \- 150\\text{ms}$ | $300\\text{ms}$ | Use WebSocket streaming models (e.g., Deepgram Nova-2) with interim transcription enabled. |
| LLM Processing (TTFT) | $150\\text{ms} \- 250\\text{ms}$ | $600\\text{ms}$ | Deploy fast inference engines (Groq, vLLM) using small, tuned instruction models (Llama-3.1-8B, Claude 3.5 Haiku, Gemini 2.0 Flash). |
| TTS Processing (TTFB) | $100\\text{ms} \- 180\\text{ms}$ | $400\\text{ms}$ | Stream audio on sentence fragments or first 3–5 tokens (e.g., Cartesia Sonic, ElevenLabs Turbo v2.5). |
| Network & Telephony Buffer | $50\\text{ms} \- 80\\text{ms}$ | $150\\text{ms}$ | Pin application deployment region to target market (e.g., AWS ap-south-1 Mumbai). |
| Total Round-Trip Latency | $500\\text{ms} \- 860\\text{ms}$ | $1950\\text{ms}+$ | Sub-800ms feels conversational; $\>1.5\\text{s}$ breaks natural flow. |

### Latency Reduction Techniques

* Speculative LLM Execution: Start processing the LLM request when STT interim results reach high confidence ($\>90\\%$), even before final VAD endpointing fires. If the user continues speaking, cancel the speculative request.  
*   
* Early First-Sentence TTS Dispatch: Do not wait for the LLM to complete its entire response. Split output tokens by clause punctuation (commas, periods) and send the first 3–5 words immediately to the TTS engine.  
*   
* Filler Audio Injections: If tool calling or state lookup adds $\>400\\text{ms}$ latency, stream short, contextual audio fillers ("Let me check that...", "Hmm, one moment...") to hold the conversational turn without leaving dead silence.  
* 

## 4\. Interruption & Turn-Taking Architecture

Handling barge-in smoothly separates amateur voice implementations from enterprise-grade systems.

USER SPEAKS WHILE AI IS PRODUCING AUDIO  
\------------------------------------------------------------------------------------  
\[AI Speaking Stream\] \----\> \[Audio Output Buffer\] \----\> \[Caller Telephone\]  
                                   |  
\[Caller Microphone\] \---\> \[Acoustic VAD (Silero)\]  
                                   | (On Voice Onset Detected)  
                                   v  
                      \+-------------------------+  
                      |   PURGE / CLEAR SIGNAL  |  
                      \+-------------------------+  
                                   |  
               \+-------------------+-------------------+  
               |                                       |  
               v                                       v  
   \[Purge Local Audio Queue\]             \[Send WSS 'clear' Event to CPaaS\]  
               |                                       |  
               v                                       v  
    \[Cancel LLM Generation\]                \[Stop Telephony Playback Instantly\]  
\------------------------------------------------------------------------------------

### Interruption Scenarios & Mitigations

1. User Barges In mid-sentence:  
2. 

   * Acoustic VAD detects speech ($\>30\\text{ms}$ energy above threshold).  
   *   
   * Orchestrator sends an immediate clear event to the telephony provider (e.g., Plivo/Exotel WebSocket clear command).  
   *   
   * The audio queue is flushed, LLM output generation is aborted, and the STT engine prioritizes the new user speech input.  
   *   
3. False Interruptions (Background noise, coughing, brief "mm-hmm"):  
4. 

   * Mitigation: Implement a two-stage confirmation window. Soft interrupt: Pause audio playback for $150\\text{ms}$. If the user speech stops within $200\\text{ms}$ (a quick "okay" or cough), resume playback from the pause point. If speech continues, execute a hard clear.  
   *   
5. Mid-Utterance Thinking Pauses ("I was absent because... uh... my fever..."):  
6. 

   * Mitigation: Do not rely solely on static silence timers. Use dynamic endpointing: lengthen silence threshold ($800\\text{ms}$) when trailing words end with conjunctions or hesitation tokens ("because", "and", "uh"), and shorten it ($300\\text{ms}$) when sentence completion syntax is detected.  
   * 

## 5\. Voice Quality & Speech Synthesis (TTS) Strategy

| Provider / Model | Latency (TTFB) | Voice Naturalness | Streaming Support | Indian English Performance | Telugu Quality | Cost Profile |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Cartesia Sonic | $\\approx 90\\text{ms} \- 120\\text{ms}$ | High | WebSocket / Chunked | Excellent | Limited / Beta | $\\$0.030 \- \\$0.060$ / 1k chars |
| ElevenLabs Turbo v2.5 | $\\approx 150\\text{ms} \- 250\\text{ms}$ | Industry Leading | WebSocket / Chunked | Excellent | Moderate | $\\$0.150 \- \\$0.300$ / 1k chars |
| Deepgram Aura | $\\approx 100\\text{ms} \- 140\\text{ms}$ | Moderate / Good | WebSocket | Good | Not Supported | $\\$0.015$ / 1k chars |
| Sarvam AI (Bulbul v2/v3) | $\\approx 200\\text{ms} \- 350\\text{ms}$ | High (Indic Native) | HTTP / WebSocket | Good | Best-in-Class (Native Pronunciation) | $\\mathbf{\\approx ₹15 \- ₹30}$ / 10k chars (\~$\\$0.018 \- \\$0.036$) |
| OpenAI Realtime Voice | $\\approx 250\\text{ms} \- 400\\text{ms}$ | High | Native WebSockets | Good | Moderate | $\\$0.060 \- \\$0.240$ / min (Speech-to-Speech) |

### Technical Verdict on TTS

* For English Phase: Cartesia Sonic or ElevenLabs Turbo v2.5 provide the optimal blend of sub-150ms Time-To-First-Audio-Byte (TTFB) and fluid conversational prosody.  
*   
* For Telugu Phase: Sarvam AI (Bulbul v3) is necessary. Global models produce unnatural pitch contours and mispronounce regional phonemes, names, and places in Telugu.  
* 

## 6\. Speech Recognition (STT) Strategy

Telephonic audio presents severe STT challenges: it is narrowband (sampled at 8kHz), compressed via lossy codecs (G.711 $\\mu$-law/A-law), and subjected to line noise and varying speaker volume.

### Speech-to-Text Benchmark Comparison

| STT Engine | Telephonic (8kHz) Accuracy | Indian Accent Handling | Code-Switching (Tanglish/Telugu-Eng) | Streaming Latency | Cost / Hour |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Deepgram Nova-2 / Nova-3 | High | High | Moderate (Trained on Indian audio) | $\<150\\text{ms}$ | $\\approx \\$0.25 \- \\$0.43$ |
| Sarvam STT | High | Native | Best-in-Class | $\\approx 200\\text{ms} \- 300\\text{ms}$ | ₹30 ($\\approx \\$0.36$) |
| OpenAI Whisper (Cloud / Local Flash) | Moderate (Needs upsampling) | Moderate | Moderate | $\>400\\text{ms}$ (Batch/Chunked) | $\\$0.36$ |
| AssemblyAI Conformer-2 | High | High | Low | $\\approx 250\\text{ms}$ | $\\$0.37$ |

### Telephonic Audio Noise Strategy

1. Audio Resampling & Conditioning: Upsample incoming 8kHz PCM to 16kHz before processing if the target STT requires 16kHz input. Apply a high-pass filter ($\<80\\text{Hz}$) to eliminate telephonic DC offset and line hum.  
2.   
3. Vocabulary Prompting / Keyterm Injection: Inject contextual domain keywords (e.g., student names, branch names like "Electronics", reason categories like "Fever", "Casual Leave") into the STT engine configuration to force accurate recognition of proper nouns.  
4. 

## 7\. LLM Reasoning & Dialogue Strategy

### End-to-End Speech-to-Speech (S2S) vs. Cascaded Pipeline

CASCADED PIPELINE (Recommended for Enterprise/Deterministic Control):  
\[Audio In\] \-\> \[STT\] \-\> \[Text Prompt \+ Guardrails\] \-\> \[LLM\] \-\> \[JSON/Tool Call State\] \-\> \[TTS\] \-\> \[Audio Out\]

END-TO-END SPEECH-TO-SPEECH (e.g., OpenAI Realtime / Gemini Live):  
\[Audio In\] \------------------------\> \[Multimodal Model\] \------------------------\> \[Audio Out\]

### Strategic Evaluation

* Speech-to-Speech (S2S) Models: Excellent natural expressiveness and low latency, but suffer from high costs ($\\approx \\$0.06 \- \\$0.30/\\text{min}$), hallucination risks, difficulty enforcing strict business logic (e.g., extracting precise student IDs), and limited support for direct Indian language telephony integration.  
*   
* Cascaded Hybrid Architecture (Recommended):  
* 

  * Orchestrator: High-speed deterministic state machine (Node.js/Python).  
  *   
  * LLM: Ultra-fast, instruction-tuned reasoning model (Groq Llama-3.1-8B, Gemini 2.0 Flash, or Claude 3.5 Haiku).  
  *   
  * Function Calling / Tool Execution: Structured output extraction (JSON) runs concurrently to extract intent ("Reason: Medical", "Return Date: 2026-08-16").  
  * 

## 8\. Unit Economics & Realistic Cost Model

### Per-Minute Operating Cost Breakdown (Production Enterprise Stack)

| Cost Center | Vendor / Solution | Per-Minute Cost (USD) | Per-Minute Cost (INR) |
| :---- | :---- | :---- | :---- |
| Telephony Transit & WSS | Plivo / Exotel (India Outbound \+ Streaming) | $\\$0.011$ | ₹0.94 |
| Streaming STT | Deepgram Nova-2 / Sarvam STT | $\\$0.005 \- \\$0.007$ | ₹0.42 \- ₹0.60 |
| LLM Reasoning | Gemini 2.0 Flash / Groq Llama-3.1-8B ($\\approx 1k$ tokens/min) | $\\$0.002 \- \\$0.004$ | ₹0.17 \- ₹0.34 |
| Streaming TTS | Cartesia / Sarvam Bulbul v3 ($\\approx 600$ chars/min) | $\\$0.003 \- \\$0.018$ | ₹0.25 \- ₹1.50 |
| Server Infra & Orchestration | AWS / Hetzner GPU/CPU Clusters | $\\$0.002$ | ₹0.17 |
| Total Estimated Cost / Min | Hybrid Enterprise AI Stack | $\\mathbf{\\$0.023 \- \\$0.042}$ | $\\mathbf{₹1.95 \- ₹3.55}$ / minute |

### Cost Comparison across Scaling Tiers

Human BPO Comparison in India: A human tele-caller in India costs approximately ₹4.00 to ₹8.00 per active conversational minute (factoring in salaries, office overhead, dialer software, and idle time). AI calling operates at ₹2.00 to ₹3.50 per minute, delivering 50%–70% cost savings alongside instantaneous horizontal concurrency.

| Campaign Volume | Total Estimated Minutes | AI Calling Platform Cost (INR) | Human Tele-Caller Cost (Est. ₹6/min) |
| :---- | :---- | :---- | :---- |
| 100 Calls (Avg 1.5 min/call) | 150 Mins | ₹375 \- ₹532 | ₹900 |
| 1,000 Calls | 1,500 Mins | ₹3,750 \- ₹5,325 | ₹9,000 |
| 10,000 Calls | 15,000 Mins | ₹37,500 \- ₹53,250 | ₹90,000 |
| 100,000 Calls | 150,000 Mins | ₹3,75,000 \- ₹5,32,500 | ₹9,000,000 |

## 9\. System Scalability & Throughput Architecture

Scaling to 1,000 concurrent active voice sessions requires a stateful, horizontally scalable architecture:

                               SYSTEM CONCURRENCY ARCHITECTURE  
                                  
\[ Campaign Trigger / CSV \] \---\> \[ Redis Queue / Celery Workers \]  
                                               |  
                                               v  
                        \+-----------------------------------------------+  
                        |          Orchestrator Cluster (Node/Go)       |  
                        |   (Stateless Audio Pipeline Controllers)      |  
                        \+-----------------------------------------------+  
                          /                    |                    \\  
                         v                     v                     v  
                \[Worker Session 1\]    \[Worker Session 2\]    \[Worker Session N\]  
                         |                     |                     |  
                \+-----------------------------------------------------------+  
                |           Distributed State & Event Storage               |  
                |   Redis Cluster (State) \<---\> PostgreSQL (Metadata/Logs)  |  
                \+-----------------------------------------------------------+

### Architectural Bottlenecks & Solutions by Scaling Tier

* 1 to 10 Concurrent Calls:  
* 

  * Single application server (Node.js/Python) maintaining WebSockets.  
  *   
  * Direct connections to third-party STT/TTS cloud APIs.  
  *   
* 10 to 100 Concurrent Calls:  
* 

  * Bottleneck: Node.js event-loop congestion caused by audio transcoding/buffering.  
  *   
  * Solution: Decouple audio streaming handlers from application logic. Use a lightweight state machine controller and manage active call states in Redis.  
  *   
* 100 to 1,000 Concurrent Calls:  
* 

  * Bottleneck: Third-party API rate limits (STT/TTS concurrency caps), telephony channel caps, and database write lock contention from stream events.  
  *   
  * Solution:  
  * 

    1. Negotiate explicit rate-limit increases (Concurrency limits $\>1,000$) with STT/TTS providers or deploy self-hosted STT/TTS containers on GPU clusters (e.g., vLLM \+ Triton Server).  
    2.   
    3. Utilize SIP Trunking with dynamic elastic channels rather than basic cloud REST APIs.  
    4.   
    5. Asynchronously push call transcripts and structured JSON results to a message queue (Kafka/RabbitMQ) for batch insertion into PostgreSQL.  
    6. 

## 10\. Regulatory & Compliance Framework in India

Navigating telecom compliance is critical for sustaining enterprise operations in India.

                          TRAI / DLT COMPLIANCE FLOWCHART  
                             
 \[ Enterprise Call Intent \]  
             |  
             \+---\> Is it Promotional / Sales?   
             |            |  
             |            \+---\> YES: Must use 140-Series Number Prefix  
             |                  Scrub list against NCPR (Do-Not-Call) Database  
             |  
             \+---\> Is it Transactional / Service (e.g., Attendance, Banking)?  
                          |  
                          \+---\> YES: Must use 160-Series Number Prefix  
                                Register Entity & Voice Script Templates on DLT Portal  
                                Explicit Prior Consent required on file

1. Digital Personal Data Protection Act (DPDPA 2023):  
2. 

   * Requires clear notice and consent mechanisms prior to processing personal data (student records, phone numbers).  
   *   
   * Call recordings and transcripts containing PII must be encrypted at rest (AES-256) and stored in in-region data centers within India.  
   *   
3. Call Recording Consent:  
4. 

   * Automated calls must begin with a clear, concise disclosure (e.g., "This is an automated AI system calling on behalf of ABC College. This call is recorded for record-keeping.").  
   *   
5. Automated Calling Time Windows:  
6. 

   * TRAI mandates commercial/promotional voice calls occur strictly between 09:00 AM and 09:00 PM IST. Transactional emergency calls are exempt but require compliant DLT template tagging.  
   * 

## 11\. Architectural Shift: English $\\rightarrow$ Telugu Transition

Adapting an AI voice system to Telugu involves more than simple translation. It requires adjusting the underlying acoustic, linguistic, and state management models.

              ENGLISH PIPELINE vs. TELUGU / TANGLISH PIPELINE

   ENGLISH PIPELINE:  
   \[8kHz Audio\] \-\> \[Deepgram Nova-2\] \-\> \[Llama-3-8B\] \-\> \[Cartesia TTS\] \-\> \[Audio Out\]

   TELUGU / TANGLISH PIPELINE:  
   \[8kHz Audio\] \-\> \[Sarvam STT / Indic VAD\] \-\> \[Language ID / Routing Layer\]  
                                                      |  
                                                      v  
   \[Audio Out\] \<- \[Sarvam Bulbul v3 TTS\] \<- \[Llama-3 \+ Telugu System Prompt\]

### Key Technical Differences

1. Acoustic & VAD Adjustments:  
2. 

   * Telugu conversational cadence features distinct vocal lengthenings and pitch inflection changes at sentence terminations (e.g., "Vasthunnara?" vs "Vasthunnaru").  
   *   
   * Standard VAD models tuned for English often misidentify vowel extensions in Telugu as silence or continued speech. VAD silence thresholds must be extended from $300\\text{ms}$ to $450\\text{ms} \- 500\\text{ms}$.  
   *   
3. Handling Code-Switching (Tanglish / Telugu \+ English):  
4. 

   * Native speakers frequently mix English words into Telugu conversation ("Nenu college ki fever valla raaleka poyanu").  
   *   
   * Generic STT models convert English words within Indic speech into phonetic non-words. You must employ a code-switching model (e.g., Sarvam STT) configured for mixed-script normalization.  
   *   
5. Phonetic Entity Extraction (Names, Numbers, Dates):  
6. 

   * LLM tokenizers often split Telugu script into numerous sub-word tokens, increasing token volume and inference latency by up to $3\\times$.  
   *   
   * Mitigation: System prompts should enforce ASCII/English output for structured data extraction (e.g., output dates as 2026-08-14 and reasons in normalized English categories) while streaming Telugu text responses to the TTS engine.  
   * 

## 12\. Competitive Landscape Analysis

| Provider / Platform | Core Differentiators | Platform Bottlenecks & Weaknesses | Indian Telephony Integration |
| :---- | :---- | :---- | :---- |
| Retell AI | Excellent low-latency orchestration, built-in turn-taking, developer-friendly Webhooks. | High markup on underlying STT/TTS; restricted customization for low-level audio buffering. | Good (Supports custom SIP Trunking / Plivo). |
| Vapi | Flexible, modular architecture; allows easy swapping of STT/LLM/TTS models. | Higher latency variations due to multiple API orchestrations; requires careful tuning. | High (Native SIP / WebSockets via Plivo & Twilio). |
| Bland AI | Native custom telephony infrastructure, built for high enterprise outbound volume. | Proprietary "black-box" model execution; limited control over exact VAD and turn-taking logic. | Moderate (Primarily optimized for US/EU PSTN). |
| Bolna.ai | Open-source platform built specifically for Indian voice AI workflows; native support for Indic TTS/STT. | Infrastructure requires active engineering maintenance at large scale. | Native (Pre-built integrations with Indian DLT, Vobiz, Exotel). |

## 13\. Critical Risks & Failure Modes Matrix

| Risk Factor | Root Cause | Impact | Mitigation Strategy |
| :---- | :---- | :---- | :---- |
| Robotic Latency Spikes | Sequential API processing, LLM cold starts, network jitter | High (Caller hangs up) | Implement speculative execution, streaming chunked TTS, and host orchestration in Mumbai (ap-south-1). |
| Barge-In Echo Loops | Telephony speaker output bleeds into microphone input | High (AI interrupts itself) | Enable strict echo cancellation (AEC) at the telephony level and enforce a $150\\text{ms}$ VAD grace period post-playback. |
| Hallucinated State Tracking | Unstructured LLM conversation drift | Medium (Corrupts reporting data) | Separate conversation generation from state tracking. Use deterministic state machines to update database values via structured tool calls. |
| DLT / Number Blocking | Calling non-consented numbers via incorrect number series | Fatal (Telecom blocking) | Secure 160-series numbers for transactional workflows, register principal entities on DLT, and maintain explicit opt-in records. |
| Poor Telugu Name Extraction | STT phonetically misinterpreting regional student names | Medium (Bad data export) | Pre-load CSV student lists into the LLM context prompt so entity recognition matches against known candidate names. |

## 14\. Recommended Master Technology Strategy

### Recommended Technology Stack

\+-----------------------------------------------------------------------------------+  
|                                PRODUCTION STACK                                   |  
|                                                                                   |  
|  \[ Telephony Layer \]       Plivo / Exotel SIP Trunking (160 Series Numbers)       |  
|  \[ Transport Protocol \]    Bidirectional WebSockets (PCM 8kHz / Slinc)             |  
|  \[ Framework Core \]        Pipecat / LiveKit Agents Engine (Python/Go)            |  
|  \[ VAD Engine \]            Silero VAD (Sub-10ms Acoustic Detection)               |  
|                                                                                   |  
|  \+-----------------------------------------------------------------------------+  |  
|  | \[ English Stack \]            \[ Telugu / Multilingual Stack \]                |  |  
|  | STT: Deepgram Nova-2         STT: Sarvam STT (Code-Switching Enabled)       |  |  
|  | LLM: Groq Llama-3.1-8B       LLM: Gemini 2.0 Flash / Claude 3.5 Haiku        |  |  
|  | TTS: Cartesia Sonic          TTS: Sarvam Bulbul v3                          |  |  
|  \+-----------------------------------------------------------------------------+  |  
|                                                                                   |  
|  \[ Application Backend \]   FastAPI / Node.js Microservices                        |  
|  \[ Cache & Session State \] Redis Cluster                                          |  
|  \[ Database & Analytics \]  PostgreSQL (JSONB Transcript & Call Result Storage)    |  
|  \[ Infrastructure Host \]   AWS India (ap-south-1 Mumbai)                          |  
\+-----------------------------------------------------------------------------------+

### Implementation Roadmap

PHASE 1: Core Architecture & English Prototype  
  │  
  ├── 1\. Deploy Pipecat/LiveKit Orchestrator on AWS Mumbai (ap-south-1)  
  ├── 2\. Provision Plivo/Exotel Indian Test Numbers with WebSockets  
  ├── 3\. Wire Pipeline: Silero VAD \-\> Deepgram STT \-\> Groq LLM \-\> Cartesia TTS  
  └── 4\. Build CSV Ingestion, Campaign Scheduler, and Structured Data Exporter

PHASE 2: Interruption Optimization & State Reliability  
  │  
  ├── 1\. Implement Dual-VAD and WebSocket frame purge signals  
  ├── 2\. Add Speculative Execution to reduce perceived turn latency to \<700ms  
  └── 3\. Implement Deterministic State Machine for Call Disposition (Answered, Busy, Reason)

PHASE 3: Telugu & Tanglish (Code-Switching) Integration  
  │  
  ├── 1\. Integrate Sarvam STT and Bulbul v3 TTS into the Pipeline  
  ├── 2\. Calibrate VAD Silence Windows (450ms) for Telugu Vocal Cadence  
  └── 3\. Train Prompt Layer for Entity Normalization (Converting spoken Telugu names/dates to English JSON)

PHASE 4: Enterprise Scale & Telecom Compliance  
  │  
  ├── 1\. Obtain DLT Registration & Provision 160-Series Number Blocks  
  ├── 2\. Scale Architecture with Redis Session Cache and Elastic SIP Trunking  
  └── 3\. Perform Load Testing up to 1,000 Concurrent Active Calls

## Architectural Synthesis

To realize your vision of an ultra-natural AI voice platform:

1. Avoid SIM Cards: Use Plivo or Exotel Cloud Telephony over WebSockets to ensure Indian compliance, full-duplex control, and scalability.  
2.   
3. Prioritize Latency: Choose high-performance components like Cartesia Sonic (English), Sarvam AI (Telugu), and Groq Llama-3.1 to keep total round-trip response time below $800\\text{ms}$.  
4.   
5. Control Interruption Logic: Build a full-duplex pipeline capable of instantly flushing stale audio buffers upon detecting user speech.  
6.   
7. Ensure Regulatory Compliance: Register your entity on the DLT portal and secure 160-series numbers for legitimate service and attendance calling.

# qwen 3.8 max

As a senior voice-AI architect and telecom engineer, I have evaluated your project requirements against the current Indian telecommunications landscape, real-time AI inference capabilities, and TRAI (Telecom Regulatory Authority of India) regulations.  
Your goal of building a "highly natural" voice agent is technically feasible today, but the Indian market presents unique regulatory and infrastructural hurdles that invalidate several standard "Western" voice-AI assumptions. Below is a research-grade, independent analysis of your project.

### 1\. Telephony: The Indian Reality

Challenge your assumption: Do not use SIM cards, eSIMs, or GSM Gateways (SIM farms) for this project.  
Using GSM gateways to route automated bulk calls bypasses standard interconnect charges and is classified as illegal telecom fraud by TRAI  
decoded.legal  
. It will result in immediate blocking of your hardware and severe legal penalties  
www.infobip.com  
.  
Best Options for India:

* Cloud Telephony (Aggregators): Providers like Exotel, Plivo, and Ozonetel are the standard for Indian Voice AI  
* caller.digital  
* . They provide DLT-compliant virtual numbers and handle the complex KYC required by Indian telecom operators (Jio, Airtel, Vi).  
* Programmable Voice APIs: Plivo offers excellent WebSocket-based "Audio Streaming" specifically designed for AI agents  
* plivo.com  
* . EnableX is another strong local contender with real-time raw audio WebSocket streaming  
* www.enablex.io  
* .  
* SIP Trunking: For high volume (10k+ calls/day), direct SIP trunks via Tata Tele or Jio Business offer the lowest per-minute rates (₹0.40–₹0.60/min) but require a Registered Telemarketer license and high upfront deposits.  
* Pricing & Routing: Twilio is generally too expensive for domestic Indian outbound calls (₹1.20–₹1.50/min)  
* exotel.com  
* . Local providers like Plivo or Exotel charge between ₹0.50 and ₹0.90 per minute for outbound mobile calls  
* caller.digital  
* ,  
* vobiz.ai  
* .

### 2\. Real-Time Voice Architecture

To achieve "human-like" quality, you must move away from standard request-response loops and adopt a Continuous Streaming Pipeline.

* Orchestration Frameworks: Do not build the pipeline from scratch. Use Pipecat (by Daily.co) or LiveKit Agents  
* www.cekura.ai  
* .  
  * *Pipecat* uses a pipeline architecture (VAD → STT → LLM → TTS) giving you granular control over barge-in logic and audio buffering  
  * thinnest.ai  
  * .  
  * *LiveKit* uses a "room" model based on WebRTC, which is superior if you plan to add multimodal features (video/avatar) later  
  * www.cekura.ai  
  * .  
* Audio Transport: You must stream raw PCM/Mulaw audio via WebSockets from the telephony provider to your media server.  
* State Management: Redis is required to maintain the independent state of thousands of concurrent calls, storing the conversation history and tool-call status for every active session.

### 3\. Latency Targets & Pipeline

In human conversation, a gap of \>1000ms feels "robotic." Your target for Time-To-First-Audio (TTFA) should be \< 600ms.  
The Latency Pipeline:

1. Endpointing (50ms): Detecting the user stopped speaking.  
2. STT Streaming (200ms): Transcribing audio *while* the user is speaking.  
3. LLM Inference (150ms): Generating the first token of the response.  
4. TTS Generation (100ms): Synthesizing the first audio chunk.  
5. Network/Playback (50ms): Sending audio back to the phone.

*Strategy:* You must use Streaming APIs for every component. Do not wait for the LLM to finish generating a full sentence before sending it to the TTS. Send chunks of 10-20 words as they are generated.

### 4\. Interruption and Turn-Taking (Barge-In)

This is the hardest engineering challenge.

* Acoustic Echo Cancellation (AEC): When the AI speaks, the user's phone mic might pick up the AI's voice. If your system doesn't filter this out, it will "hear itself" and interrupt itself.  
* Semantic Endpointing: Standard systems wait for 800ms of silence. High-end systems analyze the *transcript* to see if the user finished a thought. If the user pauses but the sentence is grammatically incomplete, the AI waits.  
* Cancel-and-Clear: When the user interrupts, the system must instantly drop the TTS buffer, cancel the LLM generation, and pass the new audio to the STT. Frameworks like Pipecat handle this "barge-in" logic natively  
* thinnest.ai  
* .

### 5\. Voice Quality (TTS)

For Indian English and eventual Telugu, naturalness is key.

* Cartesia (Sonic): Currently the latency leader (\~40ms TTFA)  
* deepgram.com  
* . It is optimized for real-time conversational AI and includes "fillers" (ums, ahs) that make it sound human.  
* ElevenLabs (Turbo v2.5 / Multilingual v2): The industry standard for emotional range and voice cloning. It supports Indian accents well and has a specific multilingual model that covers Telugu.  
* Avoid: Standard cloud TTS (AWS Polly, Google WaveNet) as they lack the "breathiness" and pacing variations of human speech.

### 6\. STT Quality for Telephony

* The Problem: Phone calls use 8kHz narrowband audio, which degrades quality.  
* The Solution: Deepgram Nova-3 or AssemblyAI Universal-1. Deepgram is specifically optimized for telephony audio and Indian accents, offering \<300ms latency  
* deepgram.com  
* ,  
* futureagi.substack.com  
* .  
* Whisper Warning: While OpenAI's Whisper is powerful, the Large-v3 model often struggles with 8kHz telephony compression and heavy Indian accents compared to specialized commercial models  
* www.hirefinn.ai  
* ,  
* novascribe.ai  
* .

### 7\. LLM Strategy

Challenge your assumption: You do *not* need a massive reasoning model for 90% of this project.

* The "College Absent" Use Case: This is a deterministic flow. You need a fast, low-latency model like Llama 3.1 70B (via Groq) or GPT-4o-mini. Groq offers inference speeds that are virtually instantaneous, which is critical for voice  
* blog.portaone.com  
* .  
* Architecture: Use a "Router" model. A fast model handles the conversation flow and turn-taking. Only route to a heavy model (Claude 3.5 Sonnet / GPT-4o) if the user asks a complex, out-of-domain question that requires deep reasoning.

### 8\. Cost Estimates (Per Minute)

Based on current API pricing  
softcery.com  
,  
inworld.ai  
,  
blog.portaone.com  
:

* Telephony (India): \~$0.012/min (₹1.00)  
* STT (Deepgram): \~$0.007/min  
* LLM (Groq/GPT-4o-mini): \~$0.005/min  
* TTS (Cartesia/ElevenLabs): \~$0.030/min  
* Total AI Cost: \~$0.054 per minute (approx. ₹4.50/min).

Scale Comparison:

* 1,000 calls (3 min avg) \= \~$162  
* 100,000 calls \= \~$16,200  
* *Human Alternative:* A human BPO agent in India costs approx. ₹15–₹25 per minute (fully loaded). AI is roughly 5x-8x cheaper and infinitely more scalable.

### 9\. Scalability Bottlenecks

* 1–10 Calls: Handled easily by a single Node.js/Python server.  
* 100 Calls: Requires load balancing and managing WebSocket file descriptors.  
* 1,000+ Calls: The bottleneck shifts to SIP Trunk Capacity and Media Server CPU. You will need a Kubernetes cluster (e.g., using LiveKit or Jitsi) to distribute the audio processing load across multiple nodes.

### 10\. Indian Legal & Telecom (Critical)

This is where most international projects fail in India.

* DLT Registration: Under TRAI regulations, every commercial/transactional call must be registered on a Distributed Ledger Technology (DLT) platform  
* thinnest.ai  
* . You must register as a "Principal Entity" (the College) and approve your "Headers" (Caller ID names) and "Teasers" (Call purpose templates).  
* Number Series: Promotional calls use the 140-series. Service/Transactional calls (like college attendance) use the 160-series or specific whitelisted headers  
* www.linkedin.com  
* .  
* AI Disclosure: Recent TRAI updates mandate that AI voice agents must disclose they are artificial if asked, or at the start of the call  
* qcall.ai  
* .  
* Penalties: Violating DND (Do Not Disturb) registries or DLT rules can attract penalties up to ₹50 Lakhs and disconnection of all telecom resources  
* conversailabs.com  
* .

### 11\. The English → Telugu Transition

Moving to Telugu is not just a "translation" task; it is a linguistic engineering challenge.

* Code-Switching (Telugish): Indian users rarely speak pure Telugu. They say, *"Nenu bus miss ayyindi, so late ga vasthanu."* Standard TTS/STT models fail here.  
* STT: You must switch to AI4Bharat's IndicConformer models, which are specifically trained on Indian code-mixed datasets and telephony audio  
* models.ai4bharat.org  
* ,  
* ai4bharat.iitm.ac.in  
* .  
* TTS: AI4Bharat’s IndicTTS and Indic-Parler-TTS offer the most natural Telugu prosody  
* github.com  
* ,  
* huggingface.co  
* . ElevenLabs Multilingual v2 is good but may struggle with specific regional slang unless you use phonetic prompting.

### 12\. Competitive Landscape Analysis

* Bland AI / Air AI: Proprietary, end-to-end platforms. Good for US markets, but they lack the deep integration with Indian DLT compliance and local SIP routing required for high connection rates in India.  
* Vapi / Retell AI: These are "orchestration layers." They allow you to plug in Twilio/Plivo and Deepgram. They are excellent for developer flexibility but require you to manage the Indian telecom compliance wrapper yourself.  
* Differentiation: The winning systems in India will be those that master Semantic Endpointing and DLT Compliance, not just those with the best voices.

### 13\. Critical Risks (The "Project Killers")

1. TRAI Blocking: If your DLT templates are not approved or you call DND numbers, your numbers will be blocked within 24 hours.  
2. Robotic Turn-Taking: If you use a fixed 800ms silence timeout, the AI will constantly interrupt people who are just thinking. You *must* implement semantic endpointing.  
3. Hallucinations: If the AI tells a student "You are expelled" because the LLM hallucinated, the liability falls on the college. You need strict "System Prompts" and "Tool Calling" constraints.  
4. Audio Degradation: 8kHz telephony audio \+ background noise (traffic/fans in India) will destroy standard Whisper models.

### 14\. Recommended Technology Strategy

Based on the research, here is the optimal stack for your prototype and MVP:

* Telephony: Plivo or Exotel. Use their WebSocket Audio Streaming APIs. Ensure your "Principal Entity" KYC is completed before writing code.  
* Orchestration Framework: Pipecat (Python). It gives you the lowest-level control over the VAD and Barge-in logic, which is essential for "natural" conversation.  
* STT: Deepgram Nova-3 (Telephony model, streaming).  
* LLM: Groq (Llama 3.1 70B). The inference speed is unmatched and critical for keeping latency under 600ms.  
* TTS: Cartesia Sonic (for lowest latency) or ElevenLabs Turbo v2.5 (for best naturalness).  
* Backend: Python (FastAPI) \+ Redis (State) \+ PostgreSQL (Campaign Data).  
* Deployment: Host your media servers in the AWS Mumbai (ap-south-1) region to minimize network latency to Indian telecom exchanges.

Final Advice: Do not start with Telugu. Spend 3 months perfecting the "Interruption/Barge-in" logic and the DLT compliance workflow in English. If the English version feels robotic, the Telugu version will be unlistenable due to the added complexity of code-mixing.

# claude approch

# **AI Voice Calling Agent — Independent Technical & Commercial Research (India, Aug 2026\)**

**How to read this:** Given the size of this brief, I'm not tagging every sentence. Instead: figures with a `(Source: ..., 2026)` note are things I found in current, dated sources — treat vendor blog numbers as *provider claims* unless I say "independent benchmark." Anything under a **"My take"** or **"Recommendation"** heading is my own inference/judgment, not a cited fact. I've flagged the places where I think your brief is making an assumption worth challenging.

---

## **0\. TL;DR — the four places I'd push back on the brief**

1. **Don't evaluate SIM/eSIM at all.** It's not a real option for this use case — no programmability, no legal outbound-calling compliance path, no concurrency, no audio streaming. The real decision is *which cloud telephony/CPaaS provider*, not telephony architecture type.  
2. **"Best latency" and "best voice quality" are not settled by picking one vendor.** The entire market has converged on a *cascaded* pipeline (STT → LLM → TTS) as the production default, specifically *because* your core requirement — structured data extraction ("why were you absent," "when will you return") — needs reliable tool-calling and auditable text at every stage. Speech-to-speech models (OpenAI Realtime, Gemini Live) are lower-latency in theory but worse at exactly the thing your admin-use-case needs most. This is the single biggest architectural decision in your brief, and I'd resolve it in the opposite direction of where "most natural conversation" intuition points.  
3. **Telugu is not a "harder version of English" — it's a different vendor stack.** None of the providers that are strong in English (Deepgram, Cartesia, ElevenLabs, AssemblyAI) have credible production Telugu. The market has a genuine India-first specialist (Sarvam AI) that is *purpose-built* for this, including Telugu-English code-switching. Plan for a stack swap, not a stack extension, in Phase 2\.  
4. **Cost math: "AI is cheaper than a human caller" is not obviously true in India at your scale.** In the US, human agents cost $35–50k/year, making AI's \~$0.05–0.25/min trivially cheaper. In India, a telecaller costs roughly ₹15,000–25,000/month and handles \~2,500–3,500 calls/month at \~3 min average — that's roughly ₹2–3.5/min *fully loaded*, which is in the same range as, or cheaper than, a well-run AI stack at low volume once you include Indian STT/TTS/LLM/telephony costs. AI's actual advantage for your use case is concurrency, 24/7 availability, consistency of data capture, and not needing to staff a calling team every semester — not raw per-minute cost. Sell it internally on that basis, not on "cheaper than a human."

---

## **1\. Telephony: the real decision is which CPaaS provider, not what "kind" of number**

### **Why SIM/eSIM is off the table**

A physical/eSIM-based approach (a phone connected to a modem/GSM gateway) has no API-level call control, no reliable concurrency beyond the number of physical SIMs you buy, no programmatic WebSocket/RTP audio access for STT/TTS integration, and critically, **no path to DLT compliance** — Indian carriers treat bulk automated calling from a personal-SIM-style number as spam and will silently block or throttle it (Source: multiple TRAI-compliance guides, 2026). This isn't a trade-off to weigh against cloud telephony; it simply doesn't do the job.

### **The real shortlist for India**

| Provider | India fit | Outbound rate (typical) | Number rental | Streaming for voice AI | DLT handling | Notes |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| **Exotel** | India/APAC-native, UL-VNO licensed telecom operator | \~₹0.80–1.00/min (Source: Exotel migration guide, 2026\) | Varies by plan | AgentStream — bidirectional WebSocket, 16-bit 8kHz PCM, \<20–50ms media latency (provider claim) | Strongest — handles DLT/DND as part of the platform (Source: caller.digital, 2026\) | Best "compliance handled for you" option; \~10–25% pricier than Plivo per-minute (Source: caller.digital, 2026\) |
| **Plivo** | Global CPaaS with strong India presence | Local outbound \~₹0.60/min (Source: awaaz.ai, 2026\) | \~₹250/month (Source: awaaz.ai, 2026\) | Native SIP trunking \+ audio streaming; explicitly integrates with LiveKit and Pipecat (Source: Plivo pricing page, 2026\) | Competent, self-managed DLT registration | Best "developer-first, cheapest to prototype on" option; 24–48hr Indian DID provisioning (Source: caller.digital, 2026\) |
| **Ozonetel** | India CCaaS \+ telephony | Unlimited-minute agent pricing on some plans (unusual model) | — | Yes | Strong | Leans more contact-center-suite than raw API; good if you eventually want agent-desktop/CCaaS features |
| **Knowlarity (Vonage)** | India-native | — | — | Yes | Strong | Similar profile to Exotel |
| **Twilio** | Global, weakest India economics | \~₹1.20–1.50/min outbound, \~₹0.50–0.80 inbound (Source: Exotel migration guide citing Twilio's own India pricing, 2026\) | — | Best-in-class docs, `<Stream>` verb, ConversationRelay | DLT is **self-managed with no platform tooling** (Source: frejun.com, 2026\) | 50–100% more expensive than India-native providers for India-domestic calls; best documentation ecosystem but that's not worth the premium here |
| **Bolna (open-source India-focused agent framework)** | India-specific, ships **Sarvam \+ Twilio-India defaults out of the box** (Source: thinnest.ai framework comparison, 2026\) | Depends on underlying telephony chosen | — | Built for exactly this stack | Handled at the framework level | Worth evaluating directly — it's the framework in this landscape closest to "built for an India \+ regional-language voice agent," see §12 |

**Reality check on the pricing figures above:** these numbers come from vendor blogs and comparison sites, not directly from a live quote. Treat them as *directionally correct, not contractual* — get an itemized INR quote from 2–3 providers before committing, since several sources explicitly warn that "quote only in USD" or vague per-minute figures are a red flag at contract stage (Source: frejun.com voice-api-india guide, 2026).

### **KYC / DLT / regulatory requirements (this is not optional paperwork — see §10 for the full legal picture)**

* Register as a **Principal Entity** on TRAI's DLT platform (PAN, GST, CIN, Aadhaar biometric auth required); one-time fee \~₹5,900 on the first TSP platform (Source: frejun.com TRAI guide, 2026).  
* Choose the correct number series: **140-series** for promotional/marketing calls, **1600-series** (was 160\) for BFSI/transactional service calls (Source: multiple TRAI-compliance guides, 2026). **Neither cleanly fits an educational-institution "why were you absent" call** — this is a genuine gray area (see §10). Get this classified correctly before your first campaign; carriers silently drop non-compliant calls rather than erroring (Source: autointerviewai.com, 2026).  
* Registration typically takes 5–10 business days when documentation is correct, longer if resubmission is needed (Source: multiple sources, 2026).

### **Recommendation**

Prototype on **Plivo** (cheapest, cleanest API, works directly with LiveKit/Pipecat, fast DID provisioning) or **Exotel** if you'd rather have DLT/compliance handled for you at a \~15–25% cost premium. Do **not** start with Twilio for India-domestic calling — its India economics are worse on every axis and its DLT tooling is weaker, and its main advantage (documentation quality) matters less once you're using LiveKit/Pipecat docs instead of Twilio's. Register DLT in parallel with prototyping — it's the long pole, and calls will silently fail without it once you leave a sandbox/test-number phase.

---

## **2\. Real-time voice architecture: the components, ranked by effect on perceived quality**

A production voice agent is a pipeline, not a model:

**Telephony (PSTN/SIP) → Audio streaming (WebSocket/RTP) → VAD → STT (streaming) → Turn/endpoint detection → LLM (streaming, with tool calling) → TTS (streaming) → Audio playback**, wrapped in session/state management that tracks conversation history, call status, and structured data extraction per call.

Ranked by how much each one actually affects whether a caller thinks they're talking to a human (my inference, based on the aggregate of what the sourced benchmarks measure and emphasize):

1. **Turn detection / endpointing** — this is the component every serious 2026 source calls "the least understood and most important" (Source: autointerviewai.com, 2026). Get this wrong and nothing else matters: the agent either talks over people or leaves robotic dead air.  
2. **TTS time-to-first-audio** — the single largest controllable contributor to perceived responsiveness (Source: codesota.com, burki.dev, 2026).  
3. **STT streaming latency \+ accuracy on telephone-quality (8kHz, noisy) audio** — most STT benchmarks are run on clean audio; production phone audio is materially harder (Source: sarvam.ai, gladia.io, 2026).  
4. **LLM time-to-first-token**, less so total generation time, since responses stream.  
5. **Barge-in / interruption handling** — technically straightforward (stop TTS playback, flush buffer) but the *policy* around it (is this a real interruption or a backchannel "mhm"?) is where quality is actually won or lost.

**My take:** most teams over-invest in "which LLM" and under-invest in turn detection and TTS latency tuning. For your project, I'd budget engineering time in the opposite proportion to where the brief's question list implies effort — turn-taking tuning and TTS provider selection will move the needle on "feels human" far more than LLM choice will.

---

## **3\. Latency: the pipeline and realistic targets**

**Human conversational turn-taking gap averages \~200ms** (Source: reactify-solutions.com citing production 2026 figures). No cascaded system fully matches this yet, but the target for "doesn't feel robotic" is generally cited as **under \~800ms** end-of-caller-speech to start-of-agent-speech, with a hard ceiling around 900ms–1.2s before callers perceive it as "the AI is thinking" (Source: retellai.com, autointerviewai.com, 2026).

Realistic 2026 component budget for a well-tuned cascaded pipeline (my synthesis of the sourced benchmarks in §5–§7, not a single vendor's number):

| Stage | Typical range (2026, tuned) |
| ----- | ----- |
| VAD / end-of-turn detection | \~200–300ms (Silero VAD baseline; semantic/prosody turn detectors add \~20ms but cut false-cutoffs) (Source: reactify-solutions.com, livekit docs, 2026\) |
| STT first-partial / streaming | 100–300ms (Deepgram Nova-3/Flux, AssemblyAI Universal-Streaming) (Source: assemblyai.com, futureagi.com, 2026\) |
| LLM time-to-first-token | 200–300ms on a fast small model via Groq; 300–600ms+ on a standard hosted frontier model (Source: neuraplus-ai, reactify-solutions.com, 2026\) |
| TTS time-to-first-audio | 40–90ms (Cartesia Sonic) to 75–300ms (ElevenLabs, depending on model tier) (Source: multiple TTS comparisons, 2026\) |
| Network/orchestration overhead | 50–200ms depending on region pinning (Source: reactify-solutions.com, 2026\) |
| **Realistic end-to-end (tuned, cascaded)** | **\~600–900ms median**, matching what Retell/Vapi/LiveKit teams report in independent 2026 tests (Source: techsy.io head-to-head test, tested.media, 2026\) |

**My take:** don't chase sub-500ms as a Phase-1 target — even the best-funded commercial platforms (Retell, Vapi) sit at 500–900ms median in independent testing, with P95 regularly exceeding 1.5s under load (Source: techsy.io, 2026). A more useful Phase-1 goal is "consistent 700–900ms with no P95 tail above \~1.5s," because *consistency* matters more to perceived quality than best-case latency (Source: retellai.com, 2026).

---

## **4\. Interruption & turn-taking**

The 2026 production pattern has three layers, and this is worth building deliberately rather than treating as a VAD afterthought:

1. **VAD (Voice Activity Detection)** — continuous per-frame confidence that incoming audio contains a voice. Silero VAD is the open-source default used across LiveKit, Pipecat, and most managed platforms.  
2. **Endpointing** — deciding *when* the user's turn has actually ended. Pure silence-threshold endpointing (typically 700–1000ms of silence) is the baseline but can't distinguish a genuine pause from someone still thinking mid-sentence (Source: autointerviewai.com, 2026).  
3. **Semantic/prosody turn detection** — the 2026 upgrade path: models that read pitch drop, rising intonation, and semantic completeness of the partial transcript to distinguish "done talking" from "thinking pause" from "backchannel" (uh-huh/mhm). LiveKit's Turn Detector v1 reports a **9.9% false-cutoff rate at a 300ms latency budget** in their own testing (Source: livekit/autointerviewai.com, 2026\) — an independently-reproducible number worth validating on your own audio before trusting it wholesale. Deepgram's **Flux** model folds end-of-turn detection directly into the STT model, claiming under 300ms median with no external VAD needed (Source: coval.ai, 2026 — vendor claim).

For interruption handling specifically: when the caller speaks while the agent is talking, the system needs to distinguish a genuine interruption ("actually, wait—") from background noise or a backchannel, then immediately stop TTS playback and discard unplayed audio if it's genuine. This is largely a solved engineering pattern in LiveKit Agents and Pipecat (both ship "adaptive interruption handling" and "false interruption" guards out of the box per their docs) — I would not try to build this from scratch.

**My take:** For your college-absence use case specifically, students will frequently pause mid-explanation ("I was... um... I had a family thing"). A silence-only endpointer will cut them off. Budget explicit tuning time for endpointing thresholds against real Indian-English and Telugu speech patterns — this is exactly the kind of thing that reads fine in a demo and breaks on real calls.

---

## **5\. Voice quality (TTS) — don't assume open-source is cheaper or better**

| Provider | Time-to-first-audio | Strength | Weakness | Telugu? |
| ----- | ----- | ----- | ----- | ----- |
| **Cartesia Sonic** | \~40–90ms (Source: multiple 2026 comparisons) | Latency leader; State Space Model architecture, not transformer-based | Voice character/emotional range slightly behind ElevenLabs; latency *spread* is wider than ElevenLabs (Source: forasoft.com, 2026\) | No |
| **ElevenLabs (Flash v2.5 / Turbo)** | \~75–300ms depending on model tier | Best voice realism/emotional expressiveness, cloning, broadest language count (32+) | Slower than Cartesia on the fast path; the highest-quality models (Multilingual v2) are 500–800ms — too slow for real-time turns | Limited — general multilingual, not Telugu-specialist |
| **Deepgram Aura-2** | \~90ms tuned | Bundled into Deepgram's Voice Agent API (single WebSocket for STT+LLM+TTS) | Newer, less proven on voice character | No |
| **Sarvam Bulbul V3** | Sub-250ms first-byte via WebSocket (provider claim, sarvam.ai 2026\) | **Purpose-built for Telugu and 10 other Indian languages** — vowel harmony, Tenglish code-switching, Indian name/number pronunciation, top-ranked in a Josh Talks blind study of 20k+ votes (provider-cited study) | Not competitive for pure-English use vs. Cartesia/ElevenLabs | **Yes — this is the answer to your Telugu TTS question** |

**My take on "open-source vs. paid":** the brief specifically asks not to assume open-source is automatically cheaper/better, and the evidence supports that skepticism — self-hosted open-weight TTS (e.g., Kokoro) is genuinely cheaper at very high volume but requires you to own GPU infrastructure, and for a project whose *entire differentiator is voice quality*, that's the wrong place to cut corners in Phase 1\. Rent a top-tier API until conversation quality is proven, then reconsider self-hosting purely as a cost optimization once volume justifies it.

**Recommendation:** Cartesia Sonic for English (latency-critical outbound calls, where every hundred milliseconds compounds into "feels robotic"). Sarvam Bulbul V3 for Telugu — there isn't a credible alternative with comparable Telugu-specific tuning (code-switching, prosody, name pronunciation) among the global providers.

---

## **6\. Speech recognition (STT) — telephone audio is the hard case, and vendor benchmarks mostly don't test it**

Independent 2026 benchmarking (Hamming.ai, 4M+ production calls) found **AssemblyAI's Universal-3 Pro Streaming faster *and* more accurate than Deepgram Nova-3** on real production call audio — 307ms P50 latency / 8.14% WER vs. Deepgram's 516ms / 9.87% (Source: assemblyai.com citing Hamming.ai, 2026 — note this is AssemblyAI's own blog citing a third-party benchmark, so treat the framing with mild skepticism even though the underlying benchmark is independent). Deepgram's counter is **Flux**, a model purpose-built for voice agents that folds end-of-turn detection into the STT step itself and posts the lowest end-of-speech latency as of mid-2026 (Source: coval.ai, futureagi.com, 2026).

Word error rate has genuinely plateaued among the top players on *clean* audio — Deepgram Nova-3, AssemblyAI Universal-3 Pro, OpenAI gpt-4o-transcribe, ElevenLabs Scribe v2, and Microsoft's MAI-Transcribe-1 all sit within 1–2 percentage points of each other on standard benchmarks (Source: coval.ai, 2026). **The real competitive surface has moved to streaming latency, end-of-turn detection, and multilingual/code-switching depth** — which is exactly where the India/Telugu question becomes decisive.

For Telugu (and Indian accents generally), **Sarvam's Saaras v3** is the standout: trained on 1M+ hours of real Indian audio specifically (not adapted from an English-first model), explicitly built for 8kHz noisy telephony audio rather than clean studio recordings, with native code-mixing/diarization support and \<150ms time-to-first-token (provider claim, sarvam.ai 2026). **Gnani.ai** is the enterprise alternative — 14M+ hours of Indian telephony training data, \#1 on 8 of 9 Indian languages on the "Kathbath Noisy" benchmark (provider claim), but it's an enterprise-only, custom-pricing platform rather than a self-serve API, which matters for a bootstrapped project.

**Recommendation:** Deepgram (Flux, for the built-in turn detection) or AssemblyAI for English. Sarvam Saaras v3 for Telugu — same reasoning as TTS above.

---

## **7\. LLM strategy — this is where I'd most directly challenge the brief's framing**

### **Does this need a large reasoning model? Mostly no.**

The actual reasoning load per turn in your use case (understand "I was absent because my grandmother was in the hospital," extract a reason, decide the next question, detect when the conversation is complete) is not a hard reasoning problem — it's closer to structured intent classification \+ slot-filling with natural-language wrapping. This is squarely in "small/fast model" territory, not "frontier reasoning model" territory.

**Groq's LPU-hosted open models** deliver genuinely large latency wins here: Llama 3.3 70B running at \~276+ tokens/sec on Groq vs. \~40–80 tokens/sec for GPT-4o on OpenAI's standard API (Source: apiscout.dev, 2026), and independent testing puts full voice-pipeline latency (STT \+ LLM \+ TTS) at \~330ms using Groq vs. \~880ms using an H100-hosted equivalent (Source: neuraplus-ai.github.io, 2026 — this is a third-party benchmark site, treat the exact numbers as illustrative rather than guaranteed on your traffic). Cost follows the same pattern: Groq's Llama 3.1 8B is $0.05/million input tokens; GPT-4o-mini is $0.15/$0.60 per million input/output (Source: baytechconsulting.com, aipricing.guru, 2026).

**Where you *do* want more model capability:** edge cases — an ambiguous or emotionally loaded response from a student, a request to speak to a human, detecting that the "reason for absence" needs escalation (e.g., mentions of a safety issue). My recommendation there isn't "use a bigger model for every turn" but "route": run the fast/cheap model by default, and have deterministic logic (keyword/intent triggers) escalate specific turns to a stronger model or to a human-handoff flow. This is standard practice in the platforms reviewed above (Vapi's server-side function calling, Bland's Pathways) and keeps both cost and latency low on the 95% of turns that don't need it.

### **Cascaded vs. speech-to-speech — resolve this explicitly, don't default to whichever sounds more "cutting edge"**

This is the architecture decision I think the brief under-weights. As of mid-2026:

* **Speech-to-speech models** (OpenAI Realtime `gpt-realtime`, Google Gemini Live) process audio-in/audio-out in a single model pass, cutting the STT→LLM→TTS latency chain. TTFA in independent testing ranges \~0.78s (xAI) to \~2.98s (Gemini 3.1 Flash Live), with OpenAI's `gpt-realtime-1.5` around 0.82s (Source: softcery.com Artificial Analysis-sourced benchmark, April 2026\) — **notably, this is not obviously faster than a well-tuned cascaded pipeline** (§3 above put tuned cascaded at 600–900ms).  
* **Cascaded pipelines** give you a text artifact at every stage — critical for exactly what your brief asks for: transcripts, structured summaries, audit logs, tool-calling for CSV-field extraction. Independent analysis is blunt about this trade-off: *"for agents that need 5+ tools with strict schema enforcement (booking, payments, healthcare intake, structured form filling), cascaded is the safer 2026 default"* (Source: futureagi.com, 2026\) — **your absent-student use case is structured-form-filling.** Cascaded also remains the enterprise/compliance default because every stage is independently observable, loggable, and redactable (Source: deepgram.com, reactify-solutions.com, 2026).  
* Speech-to-speech also currently has materially weaker language coverage — this matters directly for your Telugu roadmap, since neither OpenAI Realtime nor Gemini Live has anything close to Sarvam's Telugu depth.

**Recommendation:** cascaded architecture (STT → LLM with tool-calling → TTS), not speech-to-speech, for this entire project. This isn't a "settle for less exciting tech" call — it's the architecture every credible 2026 source converges on for exactly your requirements (structured extraction, auditability, non-English languages).

---

## **8\. Cost — worked estimates, and why "cheaper than a human" isn't automatic in India**

### **Per-minute component cost (my synthesis of the sourced ranges above, self-built cascaded stack, English)**

| Component | Range (₹/min) |
| ----- | ----- |
| Telephony (Plivo/Exotel local outbound) | ₹0.60–1.00 |
| STT (Deepgram/AssemblyAI) | ₹0.50–1.00 |
| LLM (Groq-hosted small/fast model) | ₹0.20–1.00 |
| TTS (Cartesia) | ₹1.00–2.00 |
| **Total (English, self-built)** | **\~₹3–5/min** |

For Telugu, swap in Sarvam pricing (STT ₹1.5/min flat; TTS \~₹30 per 10k characters, which works out to roughly ₹2–3/min at typical conversational pace): expect **\~₹4.50–7.50/min all-in** for Telugu, before infra/hosting overhead.

For context, if you instead *bought* a fully managed Indian voice-AI vendor (Gnani, Skit, Yellow.ai, etc.) rather than building, expect **₹4.50–9/min plus a platform fee of ₹1–6 lakh/month** at meaningful scale (Source: caller.digital, 2026\) — that's the "buy" price, and it's the reason a build-your-own approach is worth the engineering investment for a project where voice quality is the whole point and long-term unit economics matter (e.g., if you later commercialize this for other colleges).

### **Monthly cost at scale (assuming \~3 min average call, English, self-built stack, \~₹4/min all-in including infra amortization)**

| Volume | Minutes/month | Approx. monthly cost |
| ----- | ----- | ----- |
| 100 calls | \~300 | ₹1,200–1,500 |
| 1,000 calls | \~3,000 | ₹12,000–15,000 |
| 10,000 calls | \~30,000 | ₹1.2–1.5 lakh |
| 100,000 calls | \~300,000 | ₹10–13 lakh (volume discounts typically kick in, bringing effective rate toward ₹3.5–4/min) |

These are component costs only — add DLT registration (\~₹5,900 one-time \+ template fees), number rental (\~₹250–1,000/month per number), hosting/infra for your orchestration layer, storage for recordings/transcripts (marginal), and engineering time.

### **The human-calling comparison, done honestly for India**

US-context comparisons (the kind that show up in most vendor blogs) compare AI at $0.05–0.25/min to a US call-center agent at $35–50k/year — a comparison that doesn't transfer to India. A campus/admin telecaller in India typically costs **₹15,000–25,000/month fully loaded**, and can plausibly handle 80–150 calls/day depending on call complexity — at \~2,500–3,500 calls/month and \~3 min average, that's roughly **₹2–3.5/min**, which is *at or below* the low end of your self-built AI cost, and meaningfully below a bought managed platform.

**My take:** don't pitch this project on "AI is cheaper per minute than a human" in the Indian context — for your absent-student use case specifically, the real value is (a) every student gets called on the same day rather than admin staff working through a list over days, (b) structured, consistent data capture (reason, expected return date) instead of handwritten notes, (c) zero marginal cost to scale to every section/hostel simultaneously, and (d) it runs outside office hours. That's a genuinely strong pitch — it's just a different pitch than "cost savings."

---

## **9\. Scalability**

| Concurrency | What breaks first |
| ----- | ----- |
| 1 call | Nothing — this is where you validate conversation quality |
| 10 concurrent | Still trivial on any provider; useful for load-testing turn-detection tuning under real network jitter |
| 100 concurrent | Telephony provider's **channel/CPS (calls-per-second) limits** become the first bottleneck — Plivo's AI-agent tier, for example, is quoted at 50 concurrent calls / 3 CPS on its documented plan (Source: Plivo pricing page, 2026); you'll need to confirm and likely negotiate higher limits, or shard across multiple provider accounts/numbers |
| 1,000 concurrent | This is enterprise-scale telephony provisioning — direct carrier SIP trunking (the "20 lakh+ minutes/month" tier some sources describe going direct to Airtel/Jio) rather than a standard CPaaS plan (Source: caller.digital, 2026); at this point your LLM/STT/TTS provider rate limits and your own orchestration layer's horizontal scaling (stateless WebSocket workers behind a load balancer, session state in Redis/Postgres, a queue-throttled outbound dialer respecting CPS limits) become the binding constraints, not any single component |

**My take on architecture for this:** use a framework that already solves the concurrency/session-management problem rather than building it — LiveKit Agents and Pipecat both handle per-call session isolation, horizontal worker scaling, and WebRTC/SIP media at scale as first-class concerns (Source: multiple framework comparisons, 2026). Building your own WebSocket-per-call orchestrator from scratch is exactly the kind of "not your differentiator" engineering effort I'd avoid — your differentiator is conversation quality and domain flexibility, not real-time media infrastructure.

For a *campaign* use case specifically (call all absent students today), you also need a **rate-limited outbound dialer** — a queue that respects your telephony provider's CPS limit and retries on no-answer/busy according to a policy you define, independent of your real-time voice engine's own concurrency.

---

## **10\. Indian telecom/legal — this needs actual legal review, not just engineering**

I want to be direct about the limits of what I can tell you here: **this section should not be treated as legal advice, and several points below are genuinely unresolved gray areas that need a lawyer, not a search engine.**

**What's clear from current sources:**

* **DLT registration is mandatory** for any commercial/business outbound calling in India — register as a Principal Entity, register your number series and call templates, before making any calls (Source: TRAI TCCCPR framework, multiple 2026 compliance guides).  
* **TRAI classifies AI-generated voices under existing robocall/TCPA-equivalent rules** — meaning your AI calling platform is legally treated the same as any automated dialing system, not as a novel unregulated category (Source: qcall.ai, 2026).  
* **Following the 2026 IT Rules amendment, AI voice agents must self-identify as automated at the start of the call** and must not impersonate a specific real individual (Source: autointerviewai.com, 2026).  
* **DPDP Act 2023 \+ DPDP Rules 2025** (notified Nov 13, 2025\) govern what you can do with the *data* generated by the call — the recording, transcript, and any extracted fields are all "personal data." You need purpose-specific, informed consent (not just a TRAI dial-permission), a defined retention period, and — notably — **data localization**: Indian personal data should be processed/stored within India, and if you route audio through an international LLM/STT/TTS provider, you need to understand where that data actually flows (Source: caller.digital, gistly.ai, 2026). This is directly relevant to your provider choice — Sarvam explicitly markets India-only data processing/storage as a compliance feature; verify the equivalent for whichever English-stack providers you pick.  
* **Indian law is generally one-party consent for recording** (if your institution is a participant in the call, you can record it) — but DPDP's *processing* consent requirement is separate and additional to this (Source: frejun.com, caller.digital, 2026).

**The genuine gray area for your specific use case:** TRAI's number-series framework is built around **promotional (140-series)** vs **transactional/service (1600-series, BFSI-oriented)** calls. A college calling an already-enrolled student's registered number to ask about an absence is neither classic marketing nor a BFSI transaction — it's institutional/administrative outreach to an existing relationship. None of the sources I found address this category directly. **Recommendation: get this specific classification confirmed with your DLT-registration provider or telecom counsel before your first real campaign** — misclassifying it risks calls being silently dropped (wrong series) or, worse, a DND/consent complaint if students haven't been asked to opt in to this kind of automated call. A pragmatic mitigation: collect explicit consent for "the college may call you or your guardian using an automated system regarding attendance" at admission/enrollment time, which sidesteps most of the ambiguity.

* **Recording retention**: sector guides cite RBI-style retention windows (6 months–3 years) for regulated (BFSI) sectors; there's no equivalent published standard for education specifically — set a defined, disclosed retention policy rather than keeping everything indefinitely, both for DPDP compliance and to bound your own storage costs.

---

## **11\. English → Telugu: what actually changes**

This is the section where I'd tell you most directly: **treat Phase 2 as a second STT/TTS integration project, not a configuration change.**

What changes:

1. **STT and TTS providers swap entirely.** Deepgram/AssemblyAI (STT) and Cartesia/ElevenLabs (TTS) — your likely English-phase choices — do not have credible production Telugu. **Sarvam AI (Saaras v3 for STT, Bulbul V3 for TTS)** is the standout India-specific option, explicitly built and benchmarked on Telugu, with sub-250ms/sub-150ms latency claims, native Telugu-English code-switching ("Tenglish"), and correct handling of Indian names/numbers (Source: sarvam.ai product pages, 2026 — these are provider claims; validate WER/latency against your own call audio before committing, exactly as the STT benchmarking sources above caution generally).  
2. **Code-switching is not an edge case in Telugu, it's the norm.** Real conversational Telugu (as shown in Sarvam's own example transcripts) constantly mixes in English words mid-sentence ("naa account balance check cheyali"). An STT/TTS stack that treats this as noise will fail constantly; Sarvam's models are explicitly trained for this.  
3. **The LLM layer can likely stay similar** (most frontier and mid-tier LLMs handle Telugu text reasonably for understanding intent, even if you wouldn't trust them for Telugu *voice*) — but you should validate that your chosen model doesn't silently default to Hindi or standard-register Telugu when the input transcript contains colloquial or regional phrasing.  
4. **Turn-detection tuning likely needs to be redone**, not reused — Telugu sentence rhythm, pause patterns, and prosody differ from English, and the semantic/prosody turn-detection models discussed in §4 are typically trained/tuned on specific language data.  
5. **Regional variation and dialect**: sourced comparisons note real accuracy variance by region even within a single Indian language (e.g., one WER benchmark noted "Delhi Hindi" claims collapsing on "Lucknow Awadhi-influenced Hindi" in practice — Source: caller.digital, 2026). The equivalent risk exists for Telugu across Telangana/Andhra/coastal-vs-Rayalaseema variation. **Don't accept a vendor's aggregate Telugu WER claim — test against audio from your actual target population** (your parents' boutique customer base or students' likely demographic, depending on which project this is for).

**Biggest current ecosystem gap:** there is no evidence of a mature, production-proven **speech-to-speech** option for Telugu (the OpenAI Realtime / Gemini Live category) — reinforcing the cascaded-architecture recommendation in §7, since it's the only path with credible Telugu coverage at all.

---

## **12\. Competitive landscape**

Two genuinely different categories are relevant to you, and I'd resist conflating them:

**Global/English-first voice-agent platforms** (Retell AI, Vapi, Bland AI, plus the open-source LiveKit Agents/Pipecat): differentiate mainly on latency consistency, developer control, and pricing transparency — not on anything India- or Telugu-specific. Independent 2026 head-to-head testing found Retell fastest/most consistent (\~600–620ms median, \~$0.07/min), Vapi most flexible (component-level control, BYOK, effective cost $0.12–0.33/min once the full stack is added), Bland strongest for high-volume deterministic outbound flows (\~700–900ms, bundled pricing) (Source: techsy.io independent build-on-all-three test, 2026). None of these have meaningful Telugu.

**India-specific voice AI vendors** (Gnani.ai, Skit.ai, Yellow.ai, Bolna, Sarvam, Caller Digital, Squadstack): this is the more relevant comparison set for your roadmap.

* **Gnani.ai** is the largest India-headquartered player by scale (30M+ daily conversations, 40+ languages/dialects including deep Telugu coverage, 14M hours of Indian telephony training data, government IndiaAI Mission selection) — but it's enterprise-only with custom pricing, not a self-serve API you'd build a prototype on (Source: caller.digital, gnani.ai, 2026).  
* **Skit.ai** — outbound-native, strong in collections/insurance, "Hyper-Real" prosody claims (provider claim).  
* **Bolna** — the most directly relevant to your build-it-yourself plan: an open-source agent framework that **ships Sarvam \+ Twilio-India as defaults**, i.e., someone has already assembled roughly the stack this report recommends. Worth evaluating as a starting point rather than building your orchestration layer fully from scratch (Source: thinnest.ai, bolna.ai, 2026).  
* **Sarvam AI** — not a full voice-agent platform, but the STT/TTS layer underlying several of the above; you can use it directly.

**My take on what actually differentiates the strongest systems** (synthesizing across all the sourced comparisons rather than any single vendor's marketing): it is *not* raw model quality — WER and TTS MOS scores have converged across top providers. The differentiators that show up consistently across independent 2026 testing are: (1) turn-detection tuning specific to the target language/population, (2) pricing transparency vs. hidden per-component markups, and (3) for the India-specific vendors, actual dialect/regional coverage validated on real audio rather than a single benchmark language variant. Marketing claims about "hyper-real" or "indistinguishable from human" should be discounted heavily — none of the independent, third-party benchmarks I found support a categorical "indistinguishable" claim for any vendor.

---

## **13\. Critical risks — direct challenges to the project**

* **Robotic voice / high latency**: the median achievable latency in 2026 (600–900ms, per §3) is still roughly 3–4x slower than human-to-human turn-taking (\~200ms). No amount of vendor selection closes this gap entirely — manage expectations that "as close to human as technically possible" still has a perceptible, if small, robotic edge in 2026\. This isn't a solvable-with-more-budget problem; it's close to the current technical frontier.  
* **Poor turn detection / false interruptions**: this is the failure mode most likely to make the *English* version feel bad even with a good voice — and it needs real-call tuning, not just picking a good-sounding vendor.  
* **Telugu quality risk is the single biggest project risk in your roadmap**, not a secondary concern — you have exactly one credible specialist vendor (Sarvam) for the full stack; if its Telugu performance on your actual population doesn't hold up, there is no obvious second choice at comparable maturity today.  
* **Hallucination / incorrect information extraction**: for the absent-student use case, an LLM inferring a plausible-but-wrong "reason for absence" or "expected return date" is a real risk with real consequences (a college acting on fabricated data). Mitigate with strict tool-calling/function-schema enforcement (part of why cascaded \> speech-to-speech here), and a "low confidence → flag for human review" path rather than trusting every extraction.  
* **Telecom/regulatory risk**: silently dropped calls due to DLT misclassification, or a DPDP complaint from a student/parent about an unconsented automated call, are both plausible operational failure modes, not hypothetical ones — build the consent-capture step into your admin/enrollment flow now, not as an afterthought before "moving to production" (your prototype-phase "no auth needed" plan is fine for internal testing, but the *consent and DLT compliance* pieces are not something you can defer the same way — they gate whether calls connect at all).  
* **Concurrency/provider lock-in**: standard CPaaS concurrency tiers (tens of concurrent calls) will not support a "call every absent student across a large college simultaneously" campaign without either a higher-tier plan or a properly throttled dialer — plan the campaign dialer's pacing explicitly rather than assuming the telephony provider absorbs bursts for free.  
* **Cost risk at scale**: the ₹4-9/min range for a bought platform, or ₹3-7/min for a well-built one, is a real ongoing cost once you're calling thousands of students per campaign across multiple colleges — model this against your actual expected campaign frequency before assuming "AI is basically free at scale."

---

## **14\. Recommended technology strategy**

*(Recommendations, explicitly — not facts. Multiple viable alternatives are noted for each.)*

1. **Telephony**: Start on **Plivo** (cheapest, LiveKit/Pipecat-native, fast DID provisioning). Move to **Exotel** if you want DLT/compliance handled for you at a modest premium, or once call volume justifies enterprise support. Avoid Twilio for India-domestic calling.  
2. **Indian number approach**: DLT-registered virtual number via the chosen CPaaS provider — not SIM/eSIM. Start DLT Principal Entity registration in parallel with prototyping, since it's the longest lead-time item.  
3. **STT**: Deepgram (Flux, for built-in turn detection) or AssemblyAI for English. **Sarvam Saaras v3** for Telugu — no credible alternative at comparable maturity.  
4. **TTS**: **Cartesia Sonic** for English (latency-critical). **Sarvam Bulbul V3** for Telugu.  
5. **LLM strategy**: cascaded (not speech-to-speech) architecture throughout, for tool-calling reliability and Telugu support. Default to a fast/cheap model (Groq-hosted Llama 3.3-class, or GPT-4o-mini-class) for standard turns; add deterministic escalation logic (not a bigger model on every turn) for ambiguous/sensitive responses.  
6. **Real-time communication architecture**: build on **LiveKit Agents** or **Pipecat** rather than a from-scratch WebSocket orchestrator — both solve session isolation, concurrency scaling, and telephony integration as first-class problems, and both plug directly into Plivo/Exotel and every STT/TTS/LLM provider above. Consider evaluating **Bolna** directly as a starting scaffold, since it's already assembled close to this exact stack for the Indian market.  
7. **Backend architecture**: FastAPI (or equivalent) admin/API layer \+ your chosen agent framework for the real-time voice layer; a queue-based outbound campaign dialer that respects provider CPS limits; async workers for post-call processing (summary generation, structured field extraction, export).  
8. **Database**: Postgres for structured data (contacts, campaigns, calls, extracted fields, status) — this is a relational, reporting-heavy workload, not a vector/document-store problem at this stage. Object storage (S3-compatible, India-region for data-localization) for recordings.  
9. **Deployment**: containerized, deployed in an India-region cloud (Mumbai) for DPDP data-localization alignment. Managed LiveKit Cloud or Pipecat Cloud is a reasonable Phase-1 choice to avoid owning real-time media infra before you've validated conversation quality; revisit self-hosting purely as a cost optimization once volume justifies it.  
10. **Development roadmap**:  
    * **Phase 0 (now)**: single-number English prototype, no auth, cascaded pipeline (Plivo/Exotel \+ Deepgram \+ fast LLM \+ Cartesia) on LiveKit Agents or Pipecat, validated against real (not scripted) test calls for turn-detection quality.  
    * **Phase 1**: DLT registration \+ consent-capture flow \+ admin CSV upload/campaign/export UI; move from single-call testing to a rate-limited campaign dialer; nail down the absence-call domain logic (question flow, structured extraction schema, escalation rules).  
    * **Phase 2**: Telugu — swap STT/TTS to Sarvam, re-tune turn detection on real Telugu call audio, validate on your actual target population's dialect before declaring it production-ready.  
    * **Phase 3**: Tanglish code-switching, then generalize the domain layer (question flows, extraction schemas) so new use-cases beyond "absent students" are configuration, not new code.  
    * **Phase 4+**: additional Indian languages, scale-out concurrency, and only then revisit authentication/production hardening.

---

## **Sources**

This report draws on \~25 web searches across current (2026) provider documentation, independent benchmarking sites, and industry comparison articles, conducted August 2026\. Key sources cited inline include: Exotel, Plivo, and Twilio pricing/documentation pages; caller.digital, frejun.com, and awaaz.ai telephony comparison guides; TRAI-compliance guides (frejun.com, autointerviewai.com, ondial.ai, expressivr.com); DPDP Act guides (recordinglaw.com, caller.digital, gistly.ai); voice-platform comparisons (techsy.io, retellai.com, bland.ai, tested.media, alphacorp.ai); framework comparisons (thinnest.ai, forasoft.com, evalgent.com, techsy.io); STT/TTS benchmarks (assemblyai.com, futureagi.com, coval.ai, deepgram.com, gladia.io, codesota.com, burki.dev); Sarvam AI product pages; Groq/inference benchmarks (baytechconsulting.com, neuraplus-ai.github.io, apiscout.dev); cascaded-vs-speech-to-speech analysis (futureagi.com, deepgram.com, inworld.ai, reactify-solutions.com, softcery.com); cost models (inworld.ai, retellai.com, bitbytes.io, ravan.ai, caller.digital, famulor.io, klariqo.com); and Indian voice-AI competitor pages (gnani.ai, lumay.ai, vyora.ai, carmaone.ai).

**Given how fast this market is moving (several sources note major model/pricing changes within the last 1–2 months), re-verify pricing and latency figures directly against provider pages before committing to a contract — treat everything above as a well-sourced starting map, not a final quote.**

# Final approch

### 1\. The Final Technology Stack (The "Winning" Combination)

This stack is optimized for ultra-low latency (\<800ms), Indian telecom compliance, and natural turn-taking.

| Component | The Best Choice | Why it won (and what to avoid) |
| ----- | ----- | ----- |
| Telephony (India) | Exotel (Primary) or Plivo (Backup) | Avoid Twilio. Twilio is too expensive for domestic India, lacks local DLT hand-holding, and routes via international servers adding latency. Exotel/Plivo offer native Indian DIDs, WebSocket audio streaming, and DLT compliance dashboards. |
| Orchestration Framework | Pipecat (by Daily.co) | Avoid Vapi/Retell for the core engine. While Vapi/Retell are great for quick MVPs, they abstract away the audio buffer control. To achieve your goal of "human-like barge-in and turn-taking," you need Pipecat's granular, code-level control over the audio pipeline. |
| STT (English) | Deepgram (Nova-3 / Flux) | Unmatched speed (\<150ms latency). Specifically trained on telephony (8kHz) audio and handles Indian English accents far better than OpenAI Whisper. |
| STT (Telugu/Phase 2\) | Sarvam AI (Saaras) | Global models fail at "Tanglish" (Telugu-English code-switching). Sarvam is built specifically for Indic languages and mixed-script telephony audio. |
| TTS (English) | Cartesia (Sonic) or ElevenLabs (Turbo v2.5) | Cartesia wins on pure speed (\~40ms Time-To-First-Audio). ElevenLabs wins on emotional naturalness. Use Cartesia if latency is your \#1 priority; ElevenLabs if voice acting is. |
| TTS (Telugu/Phase 2\) | Sarvam AI (Bulbul V3) | ElevenLabs mispronounces Telugu names and places. Sarvam provides native prosody and handles regional dialects. |
| LLM (Brain) | Groq (Hosting Llama 3.1 8B/70B) | Avoid GPT-4o / o1 for every turn. They are too slow and expensive. Groq provides near-instant inference (crucial for voice). Use a fast model for 95% of the chat. |
| Backend API | Python (FastAPI) | Best ecosystem for AI, Pipecat integration, and asynchronous WebSocket handling. |
| State & Memory | Redis | Mandatory. You must store ephemeral call state, audio buffers, and barge-in flags in Redis for sub-millisecond access during the call. |
| Database | PostgreSQL | For persistent relational data: Campaigns, Student Lists, Call Logs, and Structured JSON Extractions. |
| Hosting / Cloud | AWS Mumbai (ap-south-1) | Non-negotiable. Hosting in the US/EU will add 200ms+ of network latency, ruining the "human" feel. Your servers must be in Mumbai. |

---

### 2\. The Core Architecture (How to achieve "Human" Quality)

To avoid the "User speaks  
→  
→ AI waits  
→  
→ AI thinks  
→  
→ AI speaks" robotic loop, you must implement a Continuous Full-Duplex Streaming Pipeline.

#### A. The "Secret Sauce": Semantic Endpointing & Barge-In

Do not rely on simple "silence timeouts" (e.g., waiting 800ms of silence to know the user is done). Humans say "um", pause to think, and take breaths.

1. Acoustic VAD (Silero): Runs locally on the audio stream to detect *any* human noise instantly.  
2. Semantic Endpointing: Send partial STT transcripts to a lightweight LLM classifier that asks: *"Is this a complete thought, or is the user just pausing?"*  
3. The Barge-In Event Bus: If the user speaks while the AI is talking, Pipecat must instantly send a clear\_buffer signal to the Telephony provider, flush the unplayed TTS audio, cancel the current LLM generation, and listen to the user.

#### B. Deterministic Logic vs. AI Logic

* AI (LLM) handles: Intent recognition, natural language generation, handling objections, and conversational empathy.  
* Code (Python/Pydantic) handles: Call state machine (Dialing  
* →  
* → Ringing  
* →  
* → Answered), Date/Time parsing, Student ID validation, and CSV export formatting. *Never let the LLM format your final database entries; it will hallucinate.*

---

### 3\. Indian Telecom & Compliance Strategy (The Make-or-Break Factor)

If you ignore this, TRAI (Telecom Regulatory Authority of India) and telecom operators will block your numbers within 48 hours.

1. SIM Cards / GSM Gateways: Absolutely forbidden. Using SIM farms for bulk automated calling is illegal telecom fraud in India. You must use enterprise Cloud Telephony (Exotel/Plivo).  
2. DLT Registration: You must register your business (or the College) as a "Principal Entity" on the telecom DLT portals.  
3. Number Series (Crucial):  
   * 140 Series: For Promotional/Marketing (Blocked on DND numbers). Do not use this.  
   * 160 Series / Standard DIDs: For Transactional/Service calls. Since a college calling its own students about attendance is a "Service/Transactional" call, you qualify for this. It bypasses DND restrictions *if* you have implicit consent.  
4. AI Disclosure: TRAI's 2025/2026 frameworks mandate that AI callers must not deceive. Your opening script must include: *"Hello, this is an automated AI assistant calling on behalf of \[College Name\]..."*  
5. Calling Hours: Strictly between 9:00 AM and 9:00 PM IST.  
6. Recording Consent: The AI must state, *"This call is being recorded for administrative purposes,"* within the first 10 seconds.

---

### 4\. The English

### →

### → Telugu Transition (Phase 2\)

The research universally agrees on one thing: An English pipeline will fail in Telugu.  
When you move to Phase 2, you do not rebuild the app; you only swap the "Speech Providers" via a Language Profile configuration.

* The Code-Switching Problem: Students will say, *"Nenu bus miss ayyindi, so late ga vasthanu."* Deepgram will turn this into gibberish.  
* The Swap:  
  * STT: Switch from Deepgram to Sarvam AI (specifically configured for Tanglish/code-mixing).  
  * TTS: Switch from Cartesia/ElevenLabs to Sarvam Bulbul V3.  
  * VAD Tuning: Telugu speakers have different cadences and elongate vowels at the end of sentences. You will need to increase your VAD silence threshold from 300ms (English) to \~500ms (Telugu) so the AI doesn't interrupt them mid-sentence.  
  * Entity Extraction: Force the LLM to output structured data (Dates, Reasons) in English/ASCII via JSON tool-calling, even if the conversation is in Telugu. This prevents database corruption.

---

### 5\. Your Step-by-Step Execution Roadmap

Do not build the web dashboard first. Build the voice loop first.

* Phase 1: The Telecom Proof (Days 1-5)  
  * Register an Exotel/Plivo account. Complete KYC using the College's entity documents.  
  * Provision a 160-series or Transactional DID.  
  * Write a basic Python script to initiate an outbound call and stream the raw 8kHz PCM audio to a local WebSocket.  
* Phase 2: The "Hello World" Voice Loop (Days 6-15)  
  * Implement Pipecat. Connect Exotel WebSockets  
  * →  
  * → Silero VAD  
  * →  
  * → Deepgram STT  
  * →  
  * → Groq (Llama 3\)  
  * →  
  * → Cartesia TTS  
  * →  
  * → back to Exotel.  
  * *Goal:* Have a 60-second conversation with the AI with zero robotic delays. Tune the barge-in logic until it feels natural.  
* Phase 3: The Business Logic (Days 16-25)  
  * Implement Pydantic schemas for the "Student Absence" workflow.  
  * Add Tool Calling: The LLM extracts {"reason": "fever", "return\_date": "2026-08-16"} and your Python backend validates the date and saves it to PostgreSQL.  
* Phase 4: The Campaign Engine & Dashboard (Days 26-40)  
  * Build the FastAPI backend to ingest CSVs.  
  * Use Redis Queues (Celery/BullMQ) to manage concurrent call limits (start with 10 concurrent, scale to 100+).  
  * Build the Next.js/React frontend for the Administrator to upload lists and download the final Excel report.  
* Phase 5: Telugu Pilot (Month 3\)  
  * Swap STT/TTS providers to Sarvam AI.  
  * Build a test dataset of 500 Tanglish audio clips to benchmark your new pipeline before deploying to students.

### Summary of the Strategy

You are not building a "Vapi clone." You are building an India-first, compliance-heavy, ultra-low-latency voice runtime using Exotel \+ Pipecat \+ Groq \+ Deepgram. This specific combination gives you the developer control needed to make the AI feel human, while respecting the strict realities of the Indian telecommunications grid.

# Tab 10

Twilo   
Livekti  
Agora  
Pipecat  
Bolna  
TEN framework  
