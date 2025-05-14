
**GeoME Chatbot API**
Introducing our Educational Navigating Chatbot, a smart, interactive guide that brings historical places and events to life through natural conversation. Whether it’s the pyramids of Egypt, the Berlin Wall, or the Independence of India, students can ask questions and instantly receive rich, engaging information tailored to their curiosity.

**1.The Opportunity**
Today’s learners are digital natives — they expect quick, intuitive access to knowledge. Yet, traditional resources can be static and overwhelming. Students often lose interest before they find what they need.

**2.The Solution**
Our chatbot transforms how students engage with history. By navigating vast historical content through simple conversation, it delivers verified facts, images, timelines, and stories in an interactive, personalized way. It can even suggest related topics, lead virtual tours, or quiz students for retention.

**3.The Benefits**

Makes history come alive through interactive, student-led exploration

Saves time by guiding learners directly to the information they seek

Boosts engagement with a modern, chat-based interface

Supports teachers by automating informational delivery and sparking curiosity

Scales easily across classrooms, museums, or learning platforms

Virtual Tour without need to travel

This isn't just a chatbot — it’s a digital historian, a personal tour guide, and a 24/7 study partner all in one.

**Workflow:**

1. User Authentication
User Sign-Up/Login:

Frontend validate credentials.

Backend verifies via authentication service provided by SWiftchat.ai.

On success User Receives a Welcome message.

2. Sending a Message

Frontend:
a.User types and sends a message,Please select the country you would like to know about?" showing up country flags to select from.
b.Once user selects a state from dropdown menu, User needs to select from another dropdown from list of cities

Message is serialized (JSON, etc.) and sent over WebSocket or via HTTP POST if not real-time.

Backend:
Validates and processes message.
Stores it in a json format.
Sends the message to the intended recipient(s) via WebSocket or push notification.

3. Receiving a Message
Recipient's Frontend:

Listens for new messages on WebSocket connection.
Displays incoming messages in real-time.
User Receives Video link and text information as Providing preference
1.History 2.Geography 3.Navigation

provides summerized text for selected options , with prompting for new session

4. Message Persistence
Messages are stored with metadata:

Sender ID, recipient ID, timestamp, read/delivery status.

5. Read Receipts & Delivery Status
Frontend:

Detects when a user views a message.

Sends "read" signal to backend.

Backend:

Updates message status.

Notifies sender of "read" or "delivered".


6. Additional Features (Optional)
Typing Indicators: Real-time "user is typing…" signals.

Presence Info: Online/offline status.

Push Notifications: For offline users.


