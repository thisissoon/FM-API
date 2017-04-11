# Base Image with OS dependencies already compiled
FROM gcr.io/soon-fm-production/api:base

# Copy Code
COPY . /fm
