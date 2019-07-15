
## USAGE

    Usage: ./webcrawler ID PASSWORD 

    - To open the debug mode: http_utility->DEBEUG_FLAG = 1
    
## The submission

Design

1. The positional arguments (username and password) are parsed and used to login to "fakebook". The connection for the HTTP is achieved with the default HTTP port, which is 80.

2. For the first GET that is sent, the response, which includes the "csrf-token" and "session-id",  is parsed and checked if it is a valid response and status is OK. If the response is not valid, the request is repeated until a correct response. The "csrf-token" and the "session-id" of the last correct response is used for the authentication toward the rest of the crawler.

3. The POST request which login the crawler into the "fakebook" if the correct username, password, and token are provided. The same approach is followed as the initial GET request. After receiving a correct response for the POST request, the server sends a new "session-id". The "session-id" of the last POST response is used for the rest of the crawler. Otherwise, the requests result in not OK but FOUND (since the previous sessions are killed).

4. The current page (initially the /fakebook/) is parsed and the links are retrieved with pattern matching. The links found in a page are put into a queue if they are already not visited. There are basically two lists, one is for queued links and the other one is for visited links. While processing the current page, the search for a secret flag is also achieved with pattern matching. 

Besides;
* If a GET request returns with 200, the next link is poped from the queued links and new GET message with the new URL but with the same tokens are sent to the server.
* If the server returns with  301 or 302, the new URL is extracted from the headers and sent with the new GET method.
* If the server returns with 403 or 404, the current page is discarded and new URL is popped from the list.
* If the server returns with 500, a GET request with the same URL is sent again.

Challenges

1.Achieving general robustness of the crawler. For example, The response messages sent by the servers can be anything including nothing. That's why the retrials of the requests while preserving the message contents but updating the correct cookies, are important.

2. Another challenge is adjusting the socket receive buffer timeouts. One way to do it is to assign predefined timeouts for the receive buffer. However, with this approach, the crawler can be very slow if the timeouts are too large. Whereas, if the timeouts are too small, the crawler will try to process an empty buffer and fail, then will send the same request over and over again. Since the response times of the server can vary a lot, static timeouts are not that useful. The approach used here is dynamically adjusting the receive timeouts according to the number of successful/unsuccessful requests.

Testing

1. After a 500 status code, the server drops the connection. The connection has to be reestablished. It means, the crawler will try many times to connect to the server before sending any request and sometimes the connection can't be established, due to many reasons. Crawler simply tries a new connection until a successful one. If the connection drops while the crawler is running, the state of the crawler does not get affected.  It resumes from where it was after a connection is established. This is tested by disabling the Internet connection, waiting for a considerable amount of time, and enabling the Internet connection again.

2.The socket receive timeout behaviors by running multiple (up to 10) crawlers at the same time. The idea is to pressure the server and make the responses delayed. The saturation point of the dynamic timeouts keeps changing depending on the number of crawler instances, which is the intended behavior. Besides, the dynamic timeout behavior also adapts differently when running the crawler in different networks the round trip time for the packets are quite different depending on the network. Based on the response delays of the server, the crawler can take from 60 second to 500 second to find the secrets.
