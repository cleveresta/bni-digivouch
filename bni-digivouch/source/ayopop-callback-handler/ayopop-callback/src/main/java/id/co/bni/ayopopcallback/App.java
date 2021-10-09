package id.co.bni.ayopopcallback;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.SQSEvent;

public class App implements RequestHandler<SQSEvent, Response> {
 
   @Override
   public Response handleRequest(SQSEvent var1, Context var2) {
      String message = "Send to SQS";
      return new Response(message, 200);
   }
}
