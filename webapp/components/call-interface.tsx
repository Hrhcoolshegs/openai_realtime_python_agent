"use client";

import React, { useState, useEffect } from "react";
import TopBar from "@/components/top-bar";
import ChecklistAndConfig from "@/components/checklist-and-config";
import SessionConfigurationPanel from "@/components/session-configuration-panel";
import Transcript from "@/components/transcript";
import FunctionCallsPanel from "@/components/function-calls-panel";
import { Item } from "@/components/types";
import handleRealtimeEvent from "@/lib/handle-realtime-event";
import PhoneNumberChecklist from "@/components/phone-number-checklist";

const CallInterface = () => {
  const [selectedPhoneNumber, setSelectedPhoneNumber] = useState("");
  const [allConfigsReady, setAllConfigsReady] = useState(false);
  const [items, setItems] = useState<Item[]>([]);
  const [callStatus, setCallStatus] = useState("disconnected");
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [twimlWebhookUrl, setTwimlWebhookUrl] = useState("");
  const [recipientPhoneNumber, setRecipientPhoneNumber] = useState("");
  const [activeCallSid, setActiveCallSid] = useState("");

  useEffect(() => {
    if (allConfigsReady && !ws) {
      const newWs = new WebSocket("ws://localhost:8081/logs");

      newWs.onopen = () => {
        console.log("Connected to logs websocket");
        setCallStatus("connected");
      };

      newWs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Received logs event:", data);
        handleRealtimeEvent(data, setItems);
      };

      newWs.onclose = () => {
        console.log("Logs websocket disconnected");
        setWs(null);
        setCallStatus("disconnected");
        setActiveCallSid("");
      };

      setWs(newWs);
    }
  }, [allConfigsReady, ws]);

  const handleMakeCall = async () => {
    if (!recipientPhoneNumber || !selectedPhoneNumber || !twimlWebhookUrl) {
      console.error("Missing required data for making call");
      return;
    }

    try {
      setCallStatus("calling");
      const response = await fetch("/api/twilio/make-call", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          from: selectedPhoneNumber,
          to: recipientPhoneNumber,
          twimlUrl: twimlWebhookUrl,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to make call");
      }

      const data = await response.json();
      setActiveCallSid(data.callSid);
      console.log("Call initiated:", data);
    } catch (error) {
      console.error("Error making call:", error);
      setCallStatus("connected");
    }
  };

  const handleEndCall = async () => {
    if (!activeCallSid) return;

    try {
      const response = await fetch("/api/twilio/end-call", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          callSid: activeCallSid,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to end call");
      }

      const data = await response.json();
      setActiveCallSid("");
      setCallStatus("connected");
      console.log("Call ended:", data);
    } catch (error) {
      console.error("Error ending call:", error);
    }
  };

  const handleTwimlUrlReady = (url: string) => {
    setTwimlWebhookUrl(url);
  };

  return (
    <div className="h-screen bg-white flex flex-col">
      <ChecklistAndConfig
        ready={allConfigsReady}
        setReady={setAllConfigsReady}
        selectedPhoneNumber={selectedPhoneNumber}
        setSelectedPhoneNumber={setSelectedPhoneNumber}
        onTwimlUrlReady={handleTwimlUrlReady}
      />
      <TopBar />
      <div className="flex-grow p-4 h-full overflow-hidden flex flex-col">
        <div className="grid grid-cols-12 gap-4 h-full">
          {/* Left Column */}
          <div className="col-span-3 flex flex-col h-full overflow-hidden">
            <SessionConfigurationPanel
              callStatus={callStatus}
              onSave={(config) => {
                if (ws && ws.readyState === WebSocket.OPEN) {
                  const updateEvent = {
                    type: "session.update",
                    session: {
                      ...config,
                    },
                  };
                  console.log("Sending update event:", updateEvent);
                  ws.send(JSON.stringify(updateEvent));
                }
              }}
            />
          </div>

          {/* Middle Column: Transcript */}
          <div className="col-span-6 flex flex-col gap-4 h-full overflow-hidden">
            <PhoneNumberChecklist
              selectedPhoneNumber={selectedPhoneNumber}
              allConfigsReady={allConfigsReady}
              setAllConfigsReady={setAllConfigsReady}
              recipientPhoneNumber={recipientPhoneNumber}
              setRecipientPhoneNumber={setRecipientPhoneNumber}
              onMakeCall={handleMakeCall}
              onEndCall={handleEndCall}
              activeCallSid={activeCallSid}
              callStatus={callStatus}
            />
            <Transcript items={items} />
          </div>

          {/* Right Column: Function Calls */}
          <div className="col-span-3 flex flex-col h-full overflow-hidden">
            <FunctionCallsPanel items={items} ws={ws} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CallInterface;