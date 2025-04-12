import http.server
import socketserver
import os

# Define the port to listen on
PORT = 5000

# Define the HTML content to serve
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CareerCompass</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Open Sans', Arial, sans-serif;
            line-height: 1.6;
            padding-top: 56px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .hero {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 80px 0;
            text-align: center;
        }
        
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .hero p {
            font-size: 1.25rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        .feature-card {
            height: 100%;
            transition: transform 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #3498db;
        }
        
        .footer {
            background-color: #2c3e50;
            color: white;
            padding: 2rem 0;
            margin-top: auto;
        }
        
        .stats-card {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .stats-number {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="#">CareerCompass</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="#">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Resume Builder</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Interview Practice</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Job Finder</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Sign In</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link btn btn-primary text-white px-3" href="#">Sign Up</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <header class="hero">
        <div class="container">
            <h1>Advance Your Career Journey</h1>
            <p class="lead">Create winning resumes, ace your interviews, and find the perfect opportunities.</p>
            <a href="#" class="btn btn-light btn-lg px-4 me-2">Get Started</a>
            <a href="#" class="btn btn-outline-light btn-lg px-4">Learn More</a>
        </div>
    </header>

    <!-- Stats Section -->
    <section class="py-5 bg-dark text-white">
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <div class="stats-card">
                        <div class="stats-number">90%</div>
                        <div>Of users improved interview performance</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stats-card">
                        <div class="stats-number">2x</div>
                        <div>Higher response rate with tailored resumes</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stats-card">
                        <div class="stats-number">10,000+</div>
                        <div>Job opportunities available</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="py-5">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="mb-3">Comprehensive Career Development Platform</h2>
                <p class="lead text-secondary">All the tools you need to succeed in your career journey</p>
            </div>
            
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card feature-card h-100 border-0 shadow-sm">
                        <div class="card-body text-center p-4">
                            <div class="feature-icon">
                                <i class="fas fa-file-alt"></i>
                            </div>
                            <h3>Smart Resume Builder</h3>
                            <p>Create tailored resumes that match specific job descriptions using AI-powered keyword analysis.</p>
                            <a href="#" class="btn btn-outline-primary mt-2">Build Resume</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card h-100 border-0 shadow-sm">
                        <div class="card-body text-center p-4">
                            <div class="feature-icon">
                                <i class="fas fa-comments"></i>
                            </div>
                            <h3>Interview Practice</h3>
                            <p>Practice with AI-generated interview questions and receive detailed feedback on your answers.</p>
                            <a href="#" class="btn btn-outline-primary mt-2">Practice Interview</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card h-100 border-0 shadow-sm">
                        <div class="card-body text-center p-4">
                            <div class="feature-icon">
                                <i class="fas fa-search"></i>
                            </div>
                            <h3>Opportunity Finder</h3>
                            <p>Discover job listings and hackathons that match your skills, interests, and career goals.</p>
                            <a href="#" class="btn btn-outline-primary mt-2">Find Opportunities</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="row">
                <div class="col-md-4 mb-4 mb-md-0">
                    <h4>CareerCompass</h4>
                    <p>Your complete career development platform</p>
                </div>
                <div class="col-md-2 mb-4 mb-md-0">
                    <h5>Features</h5>
                    <ul class="list-unstyled">
                        <li><a href="#" class="text-white">Resume Builder</a></li>
                        <li><a href="#" class="text-white">Interview Practice</a></li>
                        <li><a href="#" class="text-white">Job Finder</a></li>
                        <li><a href="#" class="text-white">Dashboard</a></li>
                    </ul>
                </div>
                <div class="col-md-2 mb-4 mb-md-0">
                    <h5>Resources</h5>
                    <ul class="list-unstyled">
                        <li><a href="#" class="text-white">Blog</a></li>
                        <li><a href="#" class="text-white">Guides</a></li>
                        <li><a href="#" class="text-white">FAQ</a></li>
                        <li><a href="#" class="text-white">Support</a></li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <h5>Stay Updated</h5>
                    <form>
                        <div class="input-group mb-3">
                            <input type="email" class="form-control" placeholder="Email Address">
                            <button class="btn btn-primary" type="button">Subscribe</button>
                        </div>
                    </form>
                    <div class="d-flex mt-3">
                        <a href="#" class="text-white me-3 fs-5"><i class="fab fa-twitter"></i></a>
                        <a href="#" class="text-white me-3 fs-5"><i class="fab fa-linkedin"></i></a>
                        <a href="#" class="text-white me-3 fs-5"><i class="fab fa-github"></i></a>
                    </div>
                </div>
            </div>
            <hr class="my-4 bg-light">
            <div class="text-center">
                <p class="mb-0">&copy; 2025 CareerCompass. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
</body>
</html>
"""

# Create a request handler
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())

# Set up and start the server
with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
    print(f"Server started on port {PORT}")
    httpd.serve_forever()