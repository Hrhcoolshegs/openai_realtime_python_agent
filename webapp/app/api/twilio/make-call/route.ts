import twilioClient from "@/lib/twilio";

export async function POST(req: Request) {
  if (!twilioClient) {
    return Response.json(
      { error: "Twilio client not initialized" },
      { status: 500 }
    );
  }

  try {
    const { from, to, twimlUrl } = await req.json();

    if (!from || !to || !twimlUrl) {
      return Response.json(
        { error: "Missing required parameters: from, to, twimlUrl" },
        { status: 400 }
      );
    }

    // Create the outbound call
    const call = await twilioClient.calls.create({
      from: from,
      to: to,
      url: twimlUrl,
      method: 'POST'
    });

    return Response.json({ 
      callSid: call.sid,
      status: call.status,
      from: call.from,
      to: call.to
    });

  } catch (error: any) {
    console.error("Error making call:", error);
    return Response.json(
      { error: `Failed to make call: ${error.message}` },
      { status: 500 }
    );
  }
}