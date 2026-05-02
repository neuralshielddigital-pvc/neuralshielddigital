# ALB Notes

- Use HTTPS listener on port 443 with ACM certificate.
- Redirect HTTP 80 to HTTPS 443.
- Point target group to ECS service on container port 8000.
