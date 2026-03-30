import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { sendChat } from "./interactionSlice";
import axios from "axios";

export default function LogInteraction() {
  const dispatch = useDispatch();
  const messages = useSelector((s) => s.interaction.messages);

  const [form, setForm] = useState({
    hcp_name: "",
    interaction_type: "",
    topics: "",
    notes: "",
  });

  const [chat, setChat] = useState("");

  const handleForm = async () => {
    await axios.post("http://localhost:8000/log-form", form);
    alert("Saved");
  };

  const handleChat = () => {
    dispatch(sendChat(chat));
    setChat("");
  };

  return (
    <div style={{ fontFamily: "Inter", padding: 20 }}>
      <h2>Log Interaction</h2>

      {/* FORM */}
      <div>
        <input placeholder="HCP Name"
          onChange={(e) => setForm({ ...form, hcp_name: e.target.value })} />

        <input placeholder="Type"
          onChange={(e) => setForm({ ...form, interaction_type: e.target.value })} />

        <input placeholder="Topics"
          onChange={(e) => setForm({ ...form, topics: e.target.value })} />

        <textarea placeholder="Notes"
          onChange={(e) => setForm({ ...form, notes: e.target.value })} />

        <button onClick={handleForm}>Save</button>
      </div>

      {/* CHAT */}
      <div style={{ marginTop: 40 }}>
        <h3>AI Chat Logger</h3>

        <input
          value={chat}
          onChange={(e) => setChat(e.target.value)}
        />
        <button onClick={handleChat}>Send</button>

        <div>
          {messages.map((m, i) => (
            <p key={i}>{m}</p>
          ))}
        </div>
      </div>
    </div>
  );
}
