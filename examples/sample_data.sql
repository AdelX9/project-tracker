-- Sample data for demo / screenshots
-- Run after 001_initial.sql

INSERT INTO projects (name, description) VALUES
    ('Website Redesign', 'Complete overhaul of the corporate website');

INSERT INTO team_members (name, role, email, capacity_hours) VALUES
    ('Alice Chen',   'Frontend Lead',    'alice@corp.com',    40),
    ('Bob Martinez', 'Backend Engineer',  'bob@corp.com',      40),
    ('Carol Kim',    'Designer',          'carol@corp.com',    32),
    ('David Petrov', 'QA Engineer',       'david@corp.com',    40),
    ('Emma Wilson',  'Project Manager',   'emma@corp.com',     20);

INSERT INTO milestones (title, description, target_date) VALUES
    ('MVP Launch',       'Core pages live with new design',  '2025-04-15'),
    ('Beta Feedback',    'Collect user feedback round 1',    '2025-05-01'),
    ('Full Launch',      'All pages migrated, old site down','2025-06-01');

INSERT INTO tasks (title, description, status, priority, assignee_id, milestone_id, estimated_hours, actual_hours, due_date, tags) VALUES
    ('Design system tokens',     'Colors, typography, spacing',    'done',        'high',     3, 1, 16, 18, '2025-03-10', 'design,tokens'),
    ('Homepage wireframe',       'Desktop + mobile layouts',       'done',        'high',     3, 1, 12,  8, '2025-03-15', 'design,wireframe'),
    ('Set up Next.js project',   'Init repo, CI, linting',         'done',        'medium',   1, 1,  4,  3, '2025-03-12', 'frontend,setup'),
    ('REST API scaffolding',     'FastAPI + auth middleware',       'done',        'high',     2, 1,  8,  6, '2025-03-14', 'backend,api'),
    ('Build header component',   'Responsive nav with dropdown',   'in_progress', 'medium',   1, 1,  6,  2, '2025-03-25', 'frontend,component'),
    ('Build footer component',   'Links, newsletter signup',       'todo',        'low',      1, 1,  4,  0, '2025-03-28', 'frontend,component'),
    ('User auth endpoints',      'Login, register, password reset','in_progress', 'critical', 2, 1, 12,  5, '2025-03-30', 'backend,auth'),
    ('Database migrations',      'User, content, media tables',    'in_review',   'high',     2, 1,  6,  7, '2025-03-20', 'backend,database'),
    ('QA test plan',             'E2E scenarios for MVP',          'in_progress', 'medium',   4, 1,  8,  3, '2025-04-01', 'qa,testing'),
    ('Content migration script', 'Move blog posts from old CMS',  'backlog',     'medium',   2, 2, 10,  0, '2025-04-20', 'backend,migration'),
    ('User feedback survey',     'Design survey in Typeform',      'backlog',     'low',      5, 2,  3,  0, '2025-04-25', 'pm,research'),
    ('Performance audit',        'Lighthouse + Core Web Vitals',   'backlog',     'high',     4, 2,  6,  0, '2025-05-01', 'qa,performance'),
    ('SEO metadata',             'Meta tags, sitemap, robots.txt', 'blocked',     'medium',   1, 3,  4,  0, '2025-05-15', 'frontend,seo'),
    ('Analytics integration',    'GA4 + custom events',            'backlog',     'medium',   2, 3,  5,  0, '2025-05-20', 'backend,analytics'),
    ('Stakeholder demo',         'Present MVP to leadership',      'todo',        'critical', 5, 1,  2,  0, '2025-04-10', 'pm,demo');
