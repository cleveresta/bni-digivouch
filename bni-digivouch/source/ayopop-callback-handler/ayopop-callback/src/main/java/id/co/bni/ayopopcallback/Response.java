package id.co.bni.ayopopcallback;

public class Response {
   private final String body;
   private final int statusCode;

   public Response(String body, int statusCode) {
      this.statusCode = statusCode;
      this.body = body;
   }

   public String getBody() {
      return this.body;
   }

   public int getStatusCode() {
      return this.statusCode;
   }
}
