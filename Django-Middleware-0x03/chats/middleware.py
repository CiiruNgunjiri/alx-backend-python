# django_middleware_0x03/middleware.py
import logging
from datetime import datetime, time
from django.http import HttpResponseForbidden

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("request_logger")
        handler = logging.FileHandler("user_requests.log")
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        user = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous"
        log_line = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_line)
        return self.get_response(request)

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define allowed access time range (6 AM to 9 PM)
        self.start_time = time(6, 0)   # 6:00 AM
        self.end_time = time(21, 0)    # 9:00 PM

    def __call__(self, request):
        now = datetime.now().time()

        # Check if current time is outside allowed range
        # Allowed times: from 6 AM (inclusive) to 9 PM (inclusive)
        is_allowed = self.start_time <= now <= self.end_time

        # Restrict access only for messaging app routes, e.g., starting with /chats or whatever path fits
        # You may customize the path check below according to your URLs:
        if request.path.startswith('/chats') or request.path.startswith('/messages'):
            if not is_allowed:
                return HttpResponseForbidden("Access to messaging is restricted between 9 PM and 6 AM.")

        # Proceed normally if allowed
        return self.get_response(request)
    
class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Store request timestamps per IP in memory
        # Structure: { ip_address: [timestamp1, timestamp2, ...] }
        self.requests_log = {}
        self.time_window = 60  # seconds (1 minute)
        self.max_requests = 5  # max messages allowed per IP in time window

    def __call__(self, request):
        # Only limit POST requests to the chat messaging endpoints
        if request.method == 'POST' and (request.path.startswith('/chats') or request.path.startswith('/messages')):
            ip = self.get_client_ip(request)
            now = time.time()

            # Clean up old requests outside the time window
            timestamps = self.requests_log.get(ip, [])
            timestamps = [ts for ts in timestamps if now - ts < self.time_window]

            if len(timestamps) >= self.max_requests:
                # Block the request if over the limit
                return HttpResponseForbidden("Message rate limit exceeded. Please wait before sending more messages.")

            # Log this request timestamp
            timestamps.append(now)
            self.requests_log[ip] = timestamps

        # Proceed with regular processing
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        # Obtain client IP address from request headers or REMOTE_ADDR
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For may contain multiple IPs, client IP is first
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define roles allowed to access
        self.allowed_roles = {'admin', 'moderator'}

    def __call__(self, request):
        user = getattr(request, 'user', None)
        
        # Check if user is authenticated and has a role attribute
        if user and user.is_authenticated:
            # Assuming your User model has a 'role' attribute as a string
            # Adjust this if your roles are stored differently (e.g., user.groups or permissions)
            user_role = getattr(user, 'role', '').lower()  
            if user_role in self.allowed_roles:
                return self.get_response(request)
        
        # If user is not authenticated or does not have allowed role, block access
        return HttpResponseForbidden("You do not have permission to perform this action.")
