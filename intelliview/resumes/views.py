# Create your views here.
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import ResumeSerializer, EducationSerializer, WorkExperienceSerializer, ProjectSerializer
from .models import Resume, Education, WorkExperience, Project
import os
import re
import PyPDF2
import docx
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            resume = serializer.save(user=request.user)
            
            # Attempt to parse the resume after saving
            try:
                self._parse_resume(resume)
            except Exception as e:
                logger.error(f"Error parsing resume: {str(e)}")
                # Continue even if parsing fails
            
            return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _parse_resume(self, resume):
        """Parse resume to extract education, work experience and projects"""
        # Extract text from the resume
        resume_text = self._extract_text_from_file(resume.file.path)
        if not resume_text:
            return
        
        # Parse sections
        sections = self._extract_sections(resume_text)
        
        # Extract and save education
        if 'education' in sections:
            education_data = self._extract_education(sections['education'])
            for edu in education_data:
                Education.objects.create(resume=resume, **edu)
        
        # Extract and save work experience
        if 'experience' in sections:
            experience_data = self._extract_work_experience(sections['experience'])
            for exp in experience_data:
                WorkExperience.objects.create(resume=resume, **exp)
        
        # Extract and save projects
        if 'projects' in sections:
            project_data = self._extract_projects(sections['projects'])
            for proj in project_data:
                Project.objects.create(resume=resume, **proj)
        
        # Mark resume as parsed
        resume.parsed = True
        resume.save()
    
    def _extract_text_from_file(self, file_path):
        """Extract text content from PDF or DOCX file"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        try:
            if ext == '.pdf':
                return self._extract_text_from_pdf(file_path)
            elif ext in ['.docx', '.doc']:
                return self._extract_text_from_docx(file_path)
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Unsupported file format: {ext}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text from file: {str(e)}")
            return ""
    
    def _extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def _extract_sections(self, text):
        """Extract sections from resume text"""
        sections = {}
        section_keywords = [
            "education", "experience", "projects", "skills", 
            "publications", "achievements", "coursework", "volunteer"
        ]
        
        # Find positions of each section
        positions = {}
        for keyword in section_keywords:
            matches = re.finditer(r'(?i)\b{}\b'.format(re.escape(keyword)), text)
            for match in matches:
                # Check if this match appears to be a section header
                line_start = text.rfind('\n', 0, match.start()) + 1 if text.rfind('\n', 0, match.start()) >= 0 else 0
                line_end = text.find('\n', match.end()) if text.find('\n', match.end()) >= 0 else len(text)
                line = text[line_start:line_end].strip()
                
                # If the keyword is a significant part of the line, consider it a header
                if len(line) <= 60 and keyword.lower() in line.lower():
                    positions[keyword.lower()] = match.start()
                    break
        
        # Sort sections by position
        sorted_sections = sorted(positions.items(), key=lambda x: x[1])
        
        # Extract text for each section
        for i, (section, start) in enumerate(sorted_sections):
            end = sorted_sections[i+1][1] if i+1 < len(sorted_sections) else len(text)
            sections[section] = text[start:end].strip()
        
        return sections
    
    def _extract_education(self, education_text):
        """Extract education details from education section"""
        education_entries = []
        
        # Split by common separators or multiple newlines
        entries = re.split(r'\n{2,}|\r\n{2,}', education_text)
        entries = [e for e in entries if len(e.strip()) > 10]  # Filter out short entries
        
        for entry in entries[1:]:  # Skip the header
            education = {}
            
            # Try to extract institution
            institution_match = re.search(r'\b(?:University|College|School|Institute|Academy)\s+(?:of\s+)?[A-Z][a-zA-Z\s]+', entry)
            if institution_match:
                education['institution'] = institution_match.group(0).strip()
            else:
                # Look for text that might be an institution name
                lines = entry.split('\n')
                for line in lines:
                    if any(word in line for word in ['University', 'College', 'School', 'Institute']):
                        education['institution'] = line.strip()
                        break
                if 'institution' not in education:
                    education['institution'] = lines[0].strip()
            
            # Extract degree
            degree_match = re.search(r'\b(?:Bachelor|Master|PhD|Doctorate|B\.S\.|M\.S\.|B\.A\.|M\.A\.|B\.E\.|M\.E\.|B\.Tech|M\.Tech)[a-zA-Z\s.]*', entry)
            if degree_match:
                education['degree'] = degree_match.group(0).strip()
            else:
                education['degree'] = "Degree"
            
            # Extract dates
            date_match = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[a-zA-Z\s.]*\d{4}\s*[-–]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|Present|Current)[a-zA-Z\s.]*\d{0,4}', entry)
            if date_match:
                date_range = date_match.group(0).strip()
                dates = re.split(r'[-–]', date_range)
                education['start_date'] = dates[0].strip()
                education['end_date'] = dates[1].strip() if len(dates) > 1 else "Present"
            else:
                year_match = re.search(r'\b20\d{2}\s*[-–]\s*(?:20\d{2}|Present|Current)', entry)
                if year_match:
                    dates = re.split(r'[-–]', year_match.group(0))
                    education['start_date'] = dates[0].strip()
                    education['end_date'] = dates[1].strip()
            
            # Extract GPA
            gpa_match = re.search(r'\bGPA\s*[:=]?\s*(\d+\.\d+|\d+)[/\s]*\d*\.?\d*', entry, re.IGNORECASE)
            if gpa_match:
                education['gpa'] = gpa_match.group(1)
            
            if 'institution' in education:
                education_entries.append(education)
        
        return education_entries
    
    def _extract_work_experience(self, experience_text):
        """Extract work experience details from experience section"""
        experience_entries = []
        
        # Split by common separators or multiple newlines
        entries = re.split(r'\n{2,}|\r\n{2,}', experience_text)
        entries = [e for e in entries if len(e.strip()) > 10]  # Filter out short entries
        
        for entry in entries[1:]:  # Skip the header
            experience = {}
            
            # Extract position
            lines = entry.split('\n')
            experience['position'] = lines[0].strip() if lines else "Position"
            
            # Extract company
            company_match = re.search(r'\b(?:at|@|with)?\s*([A-Z][a-zA-Z0-9\s&.,]+(?:Inc\.|LLC|Ltd\.|Corporation|Corp\.|Company|Co\.)?)(?:\s*[-–|])?', entry)
            if company_match:
                experience['company'] = company_match.group(1).strip()
            else:
                # Try to find a company name (often in capital letters or on the second line)
                for line in lines[1:3]:  # Check the next couple lines after position
                    if re.search(r'[A-Z][a-zA-Z0-9]+', line):
                        experience['company'] = line.strip()
                        break
                if 'company' not in experience:
                    experience['company'] = "Company"
            
            # Extract dates
            date_match = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[a-zA-Z\s.]*\d{4}\s*[-–]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|Present|Current)[a-zA-Z\s.]*\d{0,4}', entry)
            if date_match:
                date_range = date_match.group(0).strip()
                dates = re.split(r'[-–]', date_range)
                experience['start_date'] = dates[0].strip()
                experience['end_date'] = dates[1].strip() if len(dates) > 1 else "Present"
            else:
                year_match = re.search(r'\b20\d{2}\s*[-–]\s*(?:20\d{2}|Present|Current)', entry)
                if year_match:
                    dates = re.split(r'[-–]', year_match.group(0))
                    experience['start_date'] = dates[0].strip()
                    experience['end_date'] = dates[1].strip()
            
            # Extract description (the rest of the entry after the first line)
            if len(lines) > 1:
                description_lines = []
                for line in lines[1:]:
                    # Skip the line if it contains just the company or dates
                    if 'company' in experience and line.strip() == experience['company']:
                        continue
                    if 'start_date' in experience and 'end_date' in experience and experience['start_date'] in line and experience['end_date'] in line:
                        continue
                    description_lines.append(line.strip())
                experience['description'] = '\n'.join(description_lines)
            
            experience_entries.append(experience)
        
        return experience_entries
    
    def _extract_projects(self, projects_text):
        """Extract project details from projects section"""
        project_entries = []
        
        # Split by common separators or multiple newlines
        entries = re.split(r'\n{2,}|\r\n{2,}', projects_text)
        entries = [e for e in entries if len(e.strip()) > 10]  # Filter out short entries
        
        for entry in entries[1:]:  # Skip the header
            project = {}
            
            # Extract project name (usually first line)
            lines = entry.split('\n')
            project['name'] = lines[0].strip() if lines else "Project"
            
            # Extract technologies (look for technologies, tech stack, tools, etc.)
            tech_match = re.search(r'(?:Technologies|Tech Stack|Tools|Built with|Developed using|Stack)[:]\s*(.+?)(?:\n|$)', entry, re.IGNORECASE)
            if tech_match:
                project['technologies'] = tech_match.group(1).strip()
            else:
                # Look for common tech keywords
                tech_keywords = r'\b(?:Python|Java|JavaScript|React|Angular|Vue|Node|Django|Flask|Express|SQL|MongoDB|Docker|AWS|Azure|GCP|HTML|CSS|C\+\+|Swift|Kotlin|TensorFlow|PyTorch|AI|ML)\b'
                tech_matches = re.findall(tech_keywords, entry)
                if tech_matches:
                    project['technologies'] = ', '.join(tech_matches)
            
            # Extract description (everything else)
            if len(lines) > 1:
                description_lines = []
                for line in lines[1:]:
                    # Skip the line if it's just technologies
                    if 'technologies' in project and line.strip() == project['technologies']:
                        continue
                    description_lines.append(line.strip())
                project['description'] = '\n'.join(description_lines)
            
            project_entries.append(project)
        
        return project_entries

class ResumeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resumes = Resume.objects.filter(user=request.user)
        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)

class ResumeParseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        resume_id = request.data.get('resume_id')
        
        try:
            resume = Resume.objects.get(id=resume_id, user=request.user)
        except Resume.DoesNotExist:
            return Response({"detail": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Return existing parsed data if available
        serializer = ResumeSerializer(resume)
        return Response(serializer.data)

