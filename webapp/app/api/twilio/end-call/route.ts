import twilioClient from "@/lib/twilio";

export async function POST(req: Request) {
  if (!twilioClient) {
    return Response.json(
      { error: "Twilio client not initialized" },
      { status: 500 }
    );
  }

  try {
    const { callSid } = await req.json();

    if (!callSid) {
      return Response.json(
        { error: "Missing required parameter: callSid" },
        { status: 400 }
      );
    }

    // End the call by updating its status to completed
    const call = await twilioClient.calls(callSid).update({
      status: 'completed'
    });

    return Response.json({ 
      callSid: call.sid,
      status: call.status,
      message: "Call ended successfully"
    });

  } catch (error: any) {
    console.error("Error ending call:", error);
    return Response.json(
      { error: `Failed to end call: ${error.message}` },
      { status: 500 }
    );
  }
}