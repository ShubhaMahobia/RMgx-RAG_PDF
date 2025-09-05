# PDF RAG Chatbot Frontend

A modern, WhatsApp/ChatGPT-style frontend for the PDF RAG Chatbot with advanced session management.

## ✨ New Features

### 🎯 Tab-Based Sessions
- **Multiple Conversations**: Create and switch between different chat sessions
- **Independent Memory**: Each session maintains its own conversation history
- **Session Management**: Rename, delete, and organize your conversations

### 🎨 Modern Chat Interface
- **WhatsApp-Style Bubbles**: User messages (right) and assistant messages (left)
- **Smooth Animations**: Slide-in effects and typing indicators
- **Professional Styling**: Gradient backgrounds, shadows, and modern typography
- **Responsive Design**: Works beautifully on different screen sizes

### 🧭 Easy Navigation
- **Top Navigation Bar**: Access upload and manage functions from chat mode
- **Session Tabs**: Visual tabs for switching between conversations
- **Quick Actions**: New chat, rename, clear, and delete options

## 🚀 Quick Start

### Option 1: Using Python Script
```bash
cd frontend
python run_frontend.py
```

### Option 2: Direct Streamlit
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## 🎮 How to Use

### Creating New Conversations
1. Click **"➕ New Chat"** in the navigation bar
2. Each new chat gets its own tab and independent memory

### Switching Between Sessions
1. Click on any **session tab** in the navigation bar
2. The conversation history will be preserved for each session

### Managing Sessions
- **Rename**: Use the rename field in Session Settings
- **Clear**: Clear messages in current session
- **Delete**: Remove entire sessions (when multiple exist)

### Accessing Other Functions
- **Upload PDFs**: Click **"📤 Upload"** in the navigation bar
- **Manage Files**: Click **"⚙️ Manage"** in the navigation bar

## 🏗️ Architecture

### Session Structure
```python
chat_sessions = {
    "session_id": {
        "name": "Chat 1",
        "messages": [...],
        "created": datetime
    }
}
```

### Memory Management
- **LangChain Integration**: Uses ConversationBufferWindowMemory
- **Session Isolation**: Each session has independent memory
- **Automatic Persistence**: Conversations maintained across page refreshes

## 🎨 UI Features

### Message Bubbles
- **User Messages**: Blue gradient, right-aligned
- **Assistant Messages**: White background, left-aligned with avatar
- **Timestamps**: Subtle timestamps on each message
- **Source Citations**: Expandable source references

### Animations & Effects
- **Slide-in Animations**: Messages appear with smooth transitions
- **Typing Indicator**: Animated dots while assistant is thinking
- **Hover Effects**: Interactive buttons and tabs
- **Smooth Scrolling**: Auto-scroll to latest messages

### Responsive Design
- **Mobile-Friendly**: Adapts to different screen sizes
- **Flexible Layout**: Columns adjust based on content
- **Touch-Friendly**: Large touch targets for mobile users

## 🔧 Configuration

### Environment Variables
```bash
# In .env file
API_BASE_URL=http://localhost:8000
```

### Session Settings
- Access via **"⚙️ Session Settings"** expander
- Rename current session
- Create new sessions
- Clear or delete sessions

## 🎯 Key Benefits

| Feature | Before | After |
|---------|--------|-------|
| **Navigation** | Hidden sidebar | Top navigation bar |
| **Sessions** | Single conversation | Multiple tabbed sessions |
| **Memory** | Shared across all chats | Isolated per session |
| **UI Style** | Basic Streamlit | WhatsApp/ChatGPT style |
| **Animations** | None | Smooth transitions |
| **Organization** | Flat structure | Tabbed interface |

## 🐛 Troubleshooting

### Session Issues
- **Lost Sessions**: Refresh the page to reinitialize
- **Memory Not Working**: Check if backend is running and accessible
- **Tabs Not Showing**: Clear browser cache and refresh

### Performance Issues
- **Slow Loading**: Check internet connection
- **Memory Usage**: Clear old sessions regularly
- **Large Conversations**: Consider creating new sessions for long discussions

## 🚀 Future Enhancements

- [ ] **Export Conversations**: Save chats as PDF/text files
- [ ] **Search Messages**: Find specific messages across sessions
- [ ] **Voice Input**: Add speech-to-text capabilities
- [ ] **Dark Mode**: Toggle between light and dark themes
- [ ] **File Attachments**: Support for multiple file types

## 📞 Support

For issues or feature requests, please check:
1. Backend is running and accessible
2. All dependencies are installed
3. Network connectivity is stable
4. Browser cache is cleared

---

**Enjoy your enhanced PDF RAG Chatbot experience! 🎉**
