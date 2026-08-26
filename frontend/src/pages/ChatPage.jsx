/**
 * SevaSetu AI — ChatPage Component
 * Author: Rahul Jha | Made in India 🇮🇳
 *
 * Full-featured ChatGPT-style interface with:
 * - Streaming-like typing animation
 * - Voice input (Web Speech API)
 * - Text-to-speech output
 * - Multilingual support (EN / HI / MR)
 * - Query suggestions
 * - PDF export per message
 * - Mobile-responsive
 */

import { useState, useRef, useEffect, useCallback } from "react";
import { queryAPI, reportAPI, getErrorMessage } from "../services/api";
import { useAuth } from "../App";
import styles from "./ChatPage.module.css";

// ── Constants ──────────────────────────────────────────────────────────────
const SUGGESTIONS = {
  en: [
    "How to apply for Voter ID?",
    "Documents needed for Passport?",
    "PM Kisan Yojana eligibility?",
    "How to get Income Certificate?",
    "Ayushman Bharat card kaise banaye?",
    "Birth certificate online apply?",
    "PAN card for students?",
    "Domicile certificate Maharashtra?",
  ],
  hi: [
    "वोटर आईडी के लिए आवेदन कैसे करें?",
    "पैन कार्ड के लिए कौन से दस्तावेज चाहिए?",
    "आयुष्मान भारत कार्ड कैसे बनाएं?",
    "पीएम किसान योजना की पात्रता क्या है?",
    "जन्म प्रमाण पत्र ऑनलाइन कैसे बनाएं?",
    "पासपोर्ट के लिए क्या करना होगा?",
  ],
  mr: [
    "मतदार ओळखपत्र कसे मिळवायचे?",
    "पॅन कार्ड अर्ज कसा करायचा?",
    "उत्पन्न प्रमाणपत्र कसे काढायचे?",
    "आयुष्मान भारत कार्ड कसे बनवायचे?",
    "जन्म दाखला ऑनलाइन कसा मिळवायचा?",
  ],
};

const WELCOME_MSG = {
  en: `🙏 **Namaste!** I'm SevaSetu AI — your personal guide to government services and schemes.

I can help you with:
• 🗳️ Voter ID — registration, correction, download
• 💳 PAN Card — new, correction, Aadhaar linking  
• 📘 Passport — fresh, renewal, Tatkal
• 📜 Birth Certificate — registration, online apply
• 🏛️ Government schemes — PM Kisan, Ayushman Bharat, PM Awas Yojana & 100+ more
• 📋 Income, Caste & Domicile certificates

Ask me anything in English, Hindi, or Marathi! 🇮🇳`,
  hi: `🙏 **नमस्ते!** मैं SevaSetu AI हूं — सरकारी सेवाओं और योजनाओं के लिए आपका व्यक्तिगत मार्गदर्शक।

मैं इनमें मदद कर सकता हूं:
• 🗳️ वोटर आईडी • 💳 पैन कार्ड • 📘 पासपोर्ट
• 📜 जन्म प्रमाण पत्र • 🏛️ 100+ सरकारी योजनाएं
• 📋 आय, जाति और निवास प्रमाण पत्र

अंग्रेजी, हिंदी या मराठी में पूछें! 🇮🇳`,
  mr: `🙏 **नमस्कार!** मी SevaSetu AI आहे — सरकारी सेवांसाठी आपला मार्गदर्शक.

मी मदत करतो:
• 🗳️ मतदार ओळखपत्र • 💳 पॅन कार्ड • 📘 पासपोर्ट  
• 📋 उत्पन्न/जात/अधिवास प्रमाणपत्र • 🏛️ 100+ सरकारी योजना

इंग्रजी, हिंदी किंवा मराठीत विचारा! 🇮🇳`,
};

// ── Helper: Format markdown-like text ─────────────────────────────────────
function formatMessage(text) {
  if (!text) return "";
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`(.*?)`/g, "<code>$1</code>")
    .replace(/^•\s(.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br/>");
}

// ── Message Bubble ─────────────────────────────────────────────────────────
function MessageBubble({ msg, onCopyText, onExportPDF, onSpeak }) {
  const isBot = msg.role === "bot";
  const timeStr = new Date(msg.timestamp).toLocaleTimeString("en-IN", {
    hour: "2-digit", minute: "2-digit",
  });

  return (
    <div className={`${styles.msgRow} ${isBot ? styles.botRow : styles.userRow}`}>
      <div className={styles.avatar}>
        {isBot ? "🤖" : "👤"}
      </div>
      <div className={styles.msgContent}>
        <div className={`${styles.bubble} ${isBot ? styles.botBubble : styles.userBubble}`}>
          {isBot ? (
            <div
              className={styles.msgText}
              dangerouslySetInnerHTML={{ __html: formatMessage(msg.text) }}
            />
          ) : (
            <div className={styles.msgText}>{msg.text}</div>
          )}

          {/* Quick action chips for bot messages */}
          {isBot && msg.chips && (
            <div className={styles.chips}>
              {msg.chips.map((chip) => (
                <button key={chip} className={styles.chip} onClick={() => onCopyText(chip)}>
                  {chip}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className={styles.msgMeta}>
          <span className={styles.msgTime}>
            {isBot ? "SevaSetu AI" : "You"} · {timeStr}
          </span>
          {isBot && (
            <div className={styles.msgActions}>
              {msg.confidence && (
                <span className={styles.confidence}>
                  {Math.round(msg.confidence * 100)}% accurate
                </span>
              )}
              <button
                className={styles.actionBtn}
                onClick={() => navigator.clipboard.writeText(msg.text)}
                title="Copy"
              >📋</button>
              {onSpeak && (
                <button
                  className={styles.actionBtn}
                  onClick={() => onSpeak(msg.text)}
                  title="Listen"
                >🔊</button>
              )}
              {msg.queryId && (
                <button
                  className={styles.actionBtn}
                  onClick={() => onExportPDF(msg.queryId)}
                  title="Download PDF"
                >📥</button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Typing Indicator ───────────────────────────────────────────────────────
function TypingIndicator() {
  return (
    <div className={`${styles.msgRow} ${styles.botRow}`}>
      <div className={styles.avatar}>🤖</div>
      <div className={styles.typingBubble}>
        <span /><span /><span />
      </div>
    </div>
  );
}

// ── Main ChatPage ──────────────────────────────────────────────────────────
export default function ChatPage() {
  const { user } = useAuth();
  const lang     = user?.language || "en";

  const [messages, setMessages]         = useState([
    {
      id: 1,
      role: "bot",
      text: WELCOME_MSG[lang] || WELCOME_MSG.en,
      timestamp: new Date().toISOString(),
      chips: ["Voter ID", "PAN Card", "Passport", "PM Kisan", "Ayushman Bharat"],
    },
  ]);
  const [input, setInput]               = useState("");
  const [isLoading, setIsLoading]       = useState(false);
  const [isListening, setIsListening]   = useState(false);
  const [isSpeaking, setIsSpeaking]     = useState(false);
  const [error, setError]               = useState(null);
  const [suggestions, setSuggestions]   = useState(SUGGESTIONS[lang] || SUGGESTIONS.en);

  const messagesEndRef = useRef(null);
  const inputRef       = useRef(null);
  const recognitionRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // ── Send Message ─────────────────────────────────────────────────────────
  const sendMessage = useCallback(async (text) => {
    const question = (text || input).trim();
    if (!question || isLoading) return;

    setInput("");
    setError(null);

    // Add user message
    const userMsg = {
      id: Date.now(),
      role: "user",
      text: question,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res  = await queryAPI.ask(question, lang);
      const data = res.data;

      const botMsg = {
        id: Date.now() + 1,
        role: "bot",
        text: data.answer,
        timestamp: new Date().toISOString(),
        confidence: data.confidence,
        sources: data.sources,
        queryId: data.query_id,
        chips: data.sources?.slice(0, 3),
      };
      setMessages((prev) => [...prev, botMsg]);

      // Update suggestions based on category
      if (data.category) {
        const newSugs = await queryAPI.getSuggestions(data.category, lang);
        setSuggestions(newSugs.data?.suggestions || SUGGESTIONS[lang]);
      }
    } catch (err) {
      setError(getErrorMessage(err));
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "bot",
          text: "⚠️ I could not reach the SevaSetu AI service right now. Please check your connection and try again.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }, [input, isLoading, lang]);

  // ── Voice Input ──────────────────────────────────────────────────────────
  const toggleVoice = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError("Voice input not supported in this browser. Try Chrome.");
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    const langMap = { en: "en-IN", hi: "hi-IN", mr: "mr-IN" };
    recognition.lang = langMap[lang] || "en-IN";
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onstart  = () => setIsListening(true);
    recognition.onend    = () => setIsListening(false);
    recognition.onerror  = () => setIsListening(false);

    recognition.onresult = (e) => {
      const transcript = Array.from(e.results)
        .map((r) => r[0].transcript)
        .join("");
      setInput(transcript);
      if (e.results[e.results.length - 1].isFinal) {
        setIsListening(false);
        recognition.stop();
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, [isListening, lang]);

  // ── Text to Speech ────────────────────────────────────────────────────────
  const speakText = useCallback((text) => {
    if (!window.speechSynthesis) return;
    if (isSpeaking) { window.speechSynthesis.cancel(); setIsSpeaking(false); return; }

    // Strip HTML tags
    const clean = text.replace(/<[^>]+>/g, "").replace(/[•*#]/g, "");
    const utterance = new SpeechSynthesisUtterance(clean);
    const langMap = { en: "en-IN", hi: "hi-IN", mr: "mr-IN" };
    utterance.lang = langMap[lang] || "en-IN";
    utterance.rate = 0.9;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend   = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  }, [isSpeaking, lang]);

  // ── PDF Export ────────────────────────────────────────────────────────────
  const exportPDF = async (queryId) => {
    try {
      await reportAPI.downloadQueryPDF(queryId);
    } catch {
      setError("Failed to generate PDF. Please try again.");
    }
  };

  // ── Keyboard shortcut ─────────────────────────────────────────────────────
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Auto-resize textarea
  const handleInput = (e) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 160) + "px";
  };

  const clearChat = () => {
    setMessages([{
      id: Date.now(),
      role: "bot",
      text: WELCOME_MSG[lang] || WELCOME_MSG.en,
      timestamp: new Date().toISOString(),
      chips: ["Voter ID", "PAN Card", "Passport", "PM Kisan"],
    }]);
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className={styles.chatPage}>
      {/* Chat Header */}
      <div className={styles.chatHeader}>
        <div className={styles.headerLeft}>
          <div className={styles.statusDot} />
          <div>
            <h2 className={styles.headerTitle}>SevaSetu AI Assistant</h2>
            <p className={styles.headerSub}>
              Powered by Gemini + RAG · {lang === "hi" ? "हिंदी" : lang === "mr" ? "मराठी" : "English"} mode
            </p>
          </div>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.headerBtn} onClick={clearChat} title="Clear chat">
            🗑️ Clear
          </button>
          <button
            className={styles.headerBtn}
            onClick={() => reportAPI.downloadHistoryPDF()}
            title="Export history"
          >
            📥 Export
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className={styles.messagesArea}>
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            msg={msg}
            onCopyText={(text) => sendMessage(text)}
            onExportPDF={exportPDF}
            onSpeak={window.speechSynthesis ? speakText : null}
          />
        ))}
        {isLoading && <TypingIndicator />}
        {error && (
          <div className={styles.errorBanner}>
            ⚠️ {error}
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      <div className={styles.suggestionsRow}>
        {suggestions.slice(0, 4).map((s) => (
          <button
            key={s}
            className={styles.suggestion}
            onClick={() => sendMessage(s)}
            disabled={isLoading}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className={styles.inputArea}>
        <div className={styles.inputWrapper}>
          <textarea
            ref={inputRef}
            className={styles.textInput}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder={
              lang === "hi"
                ? "कोई भी सरकारी सेवा के बारे में पूछें..."
                : lang === "mr"
                ? "कोणत्याही सरकारी सेवेबद्दल विचारा..."
                : "Ask about any government service (e.g. How to apply for PAN Card?)"
            }
            rows={1}
            disabled={isLoading}
          />

          {/* Voice button */}
          <button
            className={`${styles.iconBtn} ${isListening ? styles.listening : ""}`}
            onClick={toggleVoice}
            title={isListening ? "Stop listening" : "Voice input"}
          >
            {isListening ? "🔴" : "🎤"}
          </button>

          {/* Speaking indicator */}
          {isSpeaking && (
            <button
              className={`${styles.iconBtn} ${styles.speaking}`}
              onClick={() => { window.speechSynthesis.cancel(); setIsSpeaking(false); }}
              title="Stop speaking"
            >
              🔊
            </button>
          )}

          {/* Send button */}
          <button
            className={`${styles.sendBtn} ${isLoading ? styles.sendBtnLoading : ""}`}
            onClick={() => sendMessage()}
            disabled={isLoading || !input.trim()}
          >
            {isLoading ? "⏳" : "➤"}
          </button>
        </div>

        <p className={styles.inputHint}>
          Press Enter to send · Shift+Enter for new line ·
          🎤 Voice supported · 🌐 English / हिंदी / मराठी
        </p>
      </div>
    </div>
  );
}
