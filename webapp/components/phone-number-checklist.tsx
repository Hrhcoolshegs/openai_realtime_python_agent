// PhoneNumberChecklist.tsx
"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { CheckCircle, Circle, Eye, EyeOff, Phone, PhoneOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type PhoneNumberChecklistProps = {
  selectedPhoneNumber: string;
  allConfigsReady: boolean;
  setAllConfigsReady: (ready: boolean) => void;
  recipientPhoneNumber: string;
  setRecipientPhoneNumber: (number: string) => void;
  onMakeCall: () => void;
  onEndCall: () => void;
  activeCallSid: string;
  callStatus: string;
};

const PhoneNumberChecklist: React.FC<PhoneNumberChecklistProps> = ({
  selectedPhoneNumber,
  allConfigsReady,
  setAllConfigsReady,
  recipientPhoneNumber,
  setRecipientPhoneNumber,
  onMakeCall,
  onEndCall,
  activeCallSid,
  callStatus,
}) => {
  const [isVisible, setIsVisible] = useState(true);

  const isCallActive = !!activeCallSid;
  const canMakeCall = allConfigsReady && recipientPhoneNumber.trim() !== "" && !isCallActive;
  return (
    <Card className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <span className="text-sm text-gray-500">Your Number</span>
          <div className="flex items-center">
            <span className="font-medium w-36">
              {isVisible ? selectedPhoneNumber || "None" : "••••••••••"}
            </span>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsVisible(!isVisible)}
              className="h-8 w-8"
            >
              {isVisible ? (
                <Eye className="h-4 w-4" />
              ) : (
                <EyeOff className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            {allConfigsReady ? (
              <CheckCircle className="text-green-500 w-4 h-4" />
            ) : (
              <Circle className="text-gray-400 w-4 h-4" />
            )}
            <span className="text-sm text-gray-700">
              {allConfigsReady ? "Setup Ready" : "Setup Not Ready"}
            </span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAllConfigsReady(false)}
          >
            Checklist
          </Button>
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <Input
            placeholder="Enter phone number to call (e.g., +1234567890)"
            value={recipientPhoneNumber}
            onChange={(e) => setRecipientPhoneNumber(e.target.value)}
            disabled={!allConfigsReady || isCallActive}
            className="w-full"
          />
        </div>
        <Button
          onClick={isCallActive ? onEndCall : onMakeCall}
          disabled={isCallActive ? false : !canMakeCall}
          variant={isCallActive ? "destructive" : "default"}
          className="flex items-center gap-2 min-w-[120px]"
        >
          {isCallActive ? (
            <>
              <PhoneOff className="h-4 w-4" />
              End Call
            </>
          ) : (
            <>
              <Phone className="h-4 w-4" />
              {callStatus === "calling" ? "Calling..." : "Call"}
            </>
          )}
        </Button>
      </div>
    </Card>
  );
};

export default PhoneNumberChecklist;
