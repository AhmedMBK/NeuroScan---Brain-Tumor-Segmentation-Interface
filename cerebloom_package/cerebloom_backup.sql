--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'WIN1252';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE IF EXISTS cerebloom_db;
--
-- Name: cerebloom_db; Type: DATABASE; Schema: -; Owner: cerebloom_user
--

CREATE DATABASE cerebloom_db WITH TEMPLATE = template0 ENCODING = 'WIN1252' LOCALE_PROVIDER = libc LOCALE = 'French_France.1252';


ALTER DATABASE cerebloom_db OWNER TO cerebloom_user;

\connect cerebloom_db

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'WIN1252';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: appointmentstatus; Type: TYPE; Schema: public; Owner: cerebloom_user
--

CREATE TYPE public.appointmentstatus AS ENUM (
    'SCHEDULED',
    'CONFIRMED',
    'COMPLETED',
    'CANCELLED',
    'RESCHEDULED'
);


ALTER TYPE public.appointmentstatus OWNER TO cerebloom_user;

--
-- Name: bloodtype; Type: TYPE; Schema: public; Owner: cerebloom_user
--

CREATE TYPE public.bloodtype AS ENUM (
    'A_POSITIVE',
    'A_NEGATIVE',
    'B_POSITIVE',
    'B_NEGATIVE',
    'AB_POSITIVE',
    'AB_NEGATIVE',
    'O_POSITIVE',
    'O_NEGATIVE'
);


ALTER TYPE public.bloodtype OWNER TO cerebloom_user;

--
-- Name: gender; Type: TYPE; Schema: public; Owner: cerebloom_user
--

CREATE TYPE public.gender AS ENUM (
    'MALE',
    'FEMALE'
);


ALTER TYPE public.gender OWNER TO cerebloom_user;

--
-- Name: imagemodality; Type: TYPE; Schema: public; Owner: cerebloom_user
--

CREATE TYPE public.imagemodality AS ENUM (
    'T1',
    'T1CE',
    'T2',
    'FLAIR',
    'DWI',
    'DTI'
);


ALTER TYPE public.imagemodality OWNER TO cerebloom_user;

--
-- Name: remindertype; Type: TYPE; Schema: public; Owner: cerebloom_user
--

CREATE TYPE public.remindertype AS ENUM (
    'EMAIL',
    'SMS',
    'PHONE'
);


ALTER TYPE public.remindertype OWNER TO cerebloom_user;

--
-- Name: segmentationstatus; Type: TYPE; Schema: public; Owner: cerebloom_user
--

CREATE TYPE public.segmentationstatus AS ENUM (
    'PROCESSING',
    'COMPLETED',
    'FAILED',
    'VALIDATED',
    'PENDING_REVIEW'
);


ALTER TYPE public.segmentationstatus OWNER TO cerebloom_user;

--
-- Name: treatmentstatus; Type: TYPE; Schema: public; Owner: cerebloom_user
--

CREATE TYPE public.treatmentstatus AS ENUM (
    'ACTIVE',
    'COMPLETED',
    'SUSPENDED',
    'MODIFIED'
);


ALTER TYPE public.treatmentstatus OWNER TO cerebloom_user;

--
-- Name: tumortype; Type: TYPE; Schema: public; Owner: cerebloom_user
--

CREATE TYPE public.tumortype AS ENUM (
    'NECROTIC_CORE',
    'PERITUMORAL_EDEMA',
    'ENHANCING_TUMOR',
    'WHOLE_TUMOR'
);


ALTER TYPE public.tumortype OWNER TO cerebloom_user;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: cerebloom_user
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'DOCTOR',
    'SECRETARY'
);


ALTER TYPE public.userrole OWNER TO cerebloom_user;

--
-- Name: userstatus; Type: TYPE; Schema: public; Owner: cerebloom_user
--

CREATE TYPE public.userstatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'SUSPENDED',
    'PENDING_VERIFICATION'
);


ALTER TYPE public.userstatus OWNER TO cerebloom_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ai_segmentations; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.ai_segmentations (
    id character varying(36) NOT NULL,
    patient_id character varying(36) NOT NULL,
    doctor_id character varying(36),
    image_series_id character varying(36) NOT NULL,
    status character varying(20) DEFAULT 'PROCESSING'::character varying NOT NULL,
    input_parameters json,
    segmentation_results json,
    volume_analysis json,
    tumor_classification json,
    confidence_score numeric(5,4),
    processing_time character varying(50),
    preprocessing_params json,
    postprocessing_params json,
    started_at timestamp without time zone DEFAULT now(),
    completed_at timestamp without time zone,
    validated_at timestamp without time zone
);


ALTER TABLE public.ai_segmentations OWNER TO cerebloom_user;

--
-- Name: appointment_reminders; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.appointment_reminders (
    id character varying(36) NOT NULL,
    appointment_id character varying(36) NOT NULL,
    reminder_type public.remindertype NOT NULL,
    recipient_contact character varying(255) NOT NULL,
    scheduled_time timestamp without time zone NOT NULL,
    is_sent boolean,
    sent_at timestamp without time zone,
    retry_count integer,
    created_at timestamp without time zone
);


ALTER TABLE public.appointment_reminders OWNER TO cerebloom_user;

--
-- Name: appointments; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.appointments (
    id character varying(36) NOT NULL,
    patient_id character varying(36) NOT NULL,
    doctor_id character varying(36) NOT NULL,
    scheduled_by_user_id character varying(36) NOT NULL,
    appointment_date date NOT NULL,
    appointment_time time without time zone NOT NULL,
    status public.appointmentstatus,
    notes text,
    previous_appointment_id character varying(36),
    appointment_type character varying(100),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.appointments OWNER TO cerebloom_user;

--
-- Name: COLUMN appointments.appointment_type; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.appointments.appointment_type IS 'CONSULTATION, FOLLOW_UP, EMERGENCY';


--
-- Name: doctors; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.doctors (
    id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    bio text,
    office_location character varying(200),
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.doctors OWNER TO cerebloom_user;

--
-- Name: image_series; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.image_series (
    id character varying(36) NOT NULL,
    patient_id character varying(36) NOT NULL,
    series_name character varying(200) NOT NULL,
    description text,
    image_ids json,
    acquisition_date date NOT NULL,
    technical_parameters json,
    study_instance_uid character varying(100),
    series_instance_uid character varying(100),
    slice_count integer,
    created_at timestamp without time zone
);


ALTER TABLE public.image_series OWNER TO cerebloom_user;

--
-- Name: COLUMN image_series.image_ids; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.image_series.image_ids IS 'Array of image IDs';


--
-- Name: medical_images; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.medical_images (
    id character varying(36) NOT NULL,
    patient_id character varying(36) NOT NULL,
    uploaded_by_user_id character varying(36) NOT NULL,
    modality public.imagemodality NOT NULL,
    file_path character varying(500) NOT NULL,
    file_name character varying(255) NOT NULL,
    file_size bigint NOT NULL,
    image_metadata json,
    acquisition_date date,
    body_part character varying(100),
    notes text,
    is_processed boolean,
    dicom_metadata json,
    uploaded_at timestamp without time zone
);


ALTER TABLE public.medical_images OWNER TO cerebloom_user;

--
-- Name: COLUMN medical_images.file_size; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.medical_images.file_size IS 'File size in bytes';


--
-- Name: medical_records; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.medical_records (
    id character varying(36) NOT NULL,
    patient_id character varying(36) NOT NULL,
    doctor_id character varying(36) NOT NULL,
    consultation_date date NOT NULL,
    chief_complaint text,
    symptoms text,
    physical_examination text,
    diagnosis text,
    notes text,
    vital_signs json,
    is_final boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.medical_records OWNER TO cerebloom_user;

--
-- Name: patients; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.patients (
    id character varying(36) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    date_of_birth date NOT NULL,
    gender public.gender NOT NULL,
    email character varying(255),
    phone character varying(20),
    address text,
    blood_type public.bloodtype,
    height integer,
    weight numeric(5,2),
    emergency_contact json,
    assigned_doctor_id character varying(36),
    created_by_user_id character varying(36) NOT NULL,
    medical_history json,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.patients OWNER TO cerebloom_user;

--
-- Name: COLUMN patients.height; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.patients.height IS 'Height in cm';


--
-- Name: COLUMN patients.weight; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.patients.weight IS 'Weight in kg';


--
-- Name: report_templates; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.report_templates (
    id character varying(36) NOT NULL,
    template_name character varying(200) NOT NULL,
    template_type character varying(100) NOT NULL,
    content_template text NOT NULL,
    fields_mapping json,
    category character varying(100),
    default_values json,
    is_active boolean,
    created_by_user_id character varying(36) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.report_templates OWNER TO cerebloom_user;

--
-- Name: COLUMN report_templates.template_type; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.report_templates.template_type IS 'SEGMENTATION, CONSULTATION, etc.';


--
-- Name: COLUMN report_templates.content_template; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.report_templates.content_template IS 'HTML/Markdown template';


--
-- Name: COLUMN report_templates.fields_mapping; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.report_templates.fields_mapping IS 'Dynamic fields mapping';


--
-- Name: secretaries; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.secretaries (
    id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    assigned_doctor_id character varying(36) NOT NULL,
    department character varying(100),
    office_location character varying(200),
    phone_extension character varying(10),
    responsibilities json,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.secretaries OWNER TO cerebloom_user;

--
-- Name: COLUMN secretaries.responsibilities; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.secretaries.responsibilities IS 'Liste des responsabilités';


--
-- Name: segmentation_comparisons; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.segmentation_comparisons (
    id character varying(36) NOT NULL,
    current_segmentation_id character varying(36) NOT NULL,
    previous_segmentation_id character varying(36) NOT NULL,
    volume_changes json,
    morphological_changes json,
    change_percentage numeric(6,2),
    interpretation text,
    statistical_analysis json,
    comparison_date timestamp without time zone
);


ALTER TABLE public.segmentation_comparisons OWNER TO cerebloom_user;

--
-- Name: COLUMN segmentation_comparisons.volume_changes; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.segmentation_comparisons.volume_changes IS 'Volume changes per segment';


--
-- Name: COLUMN segmentation_comparisons.morphological_changes; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.segmentation_comparisons.morphological_changes IS 'Morphological changes';


--
-- Name: COLUMN segmentation_comparisons.change_percentage; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.segmentation_comparisons.change_percentage IS 'Global change percentage';


--
-- Name: COLUMN segmentation_comparisons.interpretation; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.segmentation_comparisons.interpretation IS 'Clinical interpretation';


--
-- Name: segmentation_reports; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.segmentation_reports (
    id character varying(36) NOT NULL,
    segmentation_id character varying(36) NOT NULL,
    doctor_id character varying(36) NOT NULL,
    report_content text NOT NULL,
    findings json,
    recommendations json,
    image_attachments json,
    template_used character varying(36),
    quantitative_metrics json,
    is_final boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.segmentation_reports OWNER TO cerebloom_user;

--
-- Name: COLUMN segmentation_reports.findings; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.segmentation_reports.findings IS 'Clinical findings';


--
-- Name: COLUMN segmentation_reports.recommendations; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.segmentation_reports.recommendations IS 'Clinical recommendations';


--
-- Name: COLUMN segmentation_reports.image_attachments; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.segmentation_reports.image_attachments IS 'Segmentation images';


--
-- Name: COLUMN segmentation_reports.quantitative_metrics; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.segmentation_reports.quantitative_metrics IS 'Quantitative metrics';


--
-- Name: treatments; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.treatments (
    id character varying(36) NOT NULL,
    patient_id character varying(36) NOT NULL,
    prescribed_by_doctor_id character varying(36) NOT NULL,
    treatment_type character varying(100) NOT NULL,
    medication_name character varying(200),
    dosage character varying(100),
    frequency character varying(100),
    duration character varying(100),
    start_date date NOT NULL,
    end_date date,
    status public.treatmentstatus,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.treatments OWNER TO cerebloom_user;

--
-- Name: COLUMN treatments.treatment_type; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.treatments.treatment_type IS 'Chimiothérapie, Radiothérapie, etc.';


--
-- Name: COLUMN treatments.frequency; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.treatments.frequency IS '2 fois par jour';


--
-- Name: COLUMN treatments.duration; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.treatments.duration IS '4 semaines';


--
-- Name: tumor_segments; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.tumor_segments (
    id character varying(36) NOT NULL,
    segmentation_id character varying(36) NOT NULL,
    segment_type public.tumortype NOT NULL,
    volume_cm3 numeric(10,4) NOT NULL,
    percentage numeric(5,2) NOT NULL,
    coordinates json,
    contour_data json,
    color_code character varying(7),
    description text,
    confidence_score numeric(5,4),
    statistical_features json,
    created_at timestamp without time zone
);


ALTER TABLE public.tumor_segments OWNER TO cerebloom_user;

--
-- Name: COLUMN tumor_segments.volume_cm3; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.tumor_segments.volume_cm3 IS 'Volume in cm³';


--
-- Name: COLUMN tumor_segments.percentage; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.tumor_segments.percentage IS 'Percentage of total volume';


--
-- Name: COLUMN tumor_segments.coordinates; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.tumor_segments.coordinates IS '3D coordinates';


--
-- Name: COLUMN tumor_segments.contour_data; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.tumor_segments.contour_data IS 'Contour data';


--
-- Name: COLUMN tumor_segments.color_code; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.tumor_segments.color_code IS 'Hex color code like #FF0000';


--
-- Name: user_credentials; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.user_credentials (
    user_id character varying(36) NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    salt character varying(255) NOT NULL,
    last_login timestamp without time zone,
    failed_login_attempts integer,
    is_locked boolean,
    locked_until timestamp without time zone,
    reset_token character varying(255),
    token_expires_at timestamp without time zone
);


ALTER TABLE public.user_credentials OWNER TO cerebloom_user;

--
-- Name: user_permissions; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.user_permissions (
    user_id character varying(36) NOT NULL,
    can_view_patients boolean,
    can_create_patients boolean,
    can_edit_patients boolean,
    can_delete_patients boolean,
    can_view_segmentations boolean,
    can_create_segmentations boolean,
    can_validate_segmentations boolean,
    can_manage_appointments boolean,
    can_manage_users boolean,
    can_view_reports boolean,
    can_export_data boolean,
    custom_permissions json
);


ALTER TABLE public.user_permissions OWNER TO cerebloom_user;

--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.user_sessions (
    session_id character varying(255) NOT NULL,
    user_id character varying(36) NOT NULL,
    created_at timestamp without time zone,
    expires_at timestamp without time zone NOT NULL,
    ip_address character varying(45),
    user_agent text,
    is_active boolean,
    last_activity timestamp without time zone
);


ALTER TABLE public.user_sessions OWNER TO cerebloom_user;

--
-- Name: users; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.users (
    id character varying(36) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(20),
    role public.userrole NOT NULL,
    status public.userstatus,
    profile_picture character varying(500),
    employee_id character varying(50),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying(36),
    assigned_doctor_id character varying(36)
);


ALTER TABLE public.users OWNER TO cerebloom_user;

--
-- Name: COLUMN users.assigned_doctor_id; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.users.assigned_doctor_id IS 'Pour les secrétaires: médecin assigné';


--
-- Name: volumetric_analysis; Type: TABLE; Schema: public; Owner: cerebloom_user
--

CREATE TABLE public.volumetric_analysis (
    id character varying(36) NOT NULL,
    segmentation_id character varying(36) NOT NULL,
    total_tumor_volume numeric(10,4) NOT NULL,
    necrotic_core_volume numeric(10,4),
    peritumoral_edema_volume numeric(10,4),
    enhancing_tumor_volume numeric(10,4),
    evolution_data json,
    comparison_previous json,
    tumor_burden_index numeric(8,4),
    growth_rate_analysis json,
    analysis_date timestamp without time zone
);


ALTER TABLE public.volumetric_analysis OWNER TO cerebloom_user;

--
-- Name: COLUMN volumetric_analysis.total_tumor_volume; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.volumetric_analysis.total_tumor_volume IS 'Total volume in cm³';


--
-- Name: COLUMN volumetric_analysis.evolution_data; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.volumetric_analysis.evolution_data IS 'Temporal evolution data';


--
-- Name: COLUMN volumetric_analysis.comparison_previous; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.volumetric_analysis.comparison_previous IS 'Comparison with previous exam';


--
-- Name: COLUMN volumetric_analysis.tumor_burden_index; Type: COMMENT; Schema: public; Owner: cerebloom_user
--

COMMENT ON COLUMN public.volumetric_analysis.tumor_burden_index IS 'Tumor burden index';


--
-- Data for Name: ai_segmentations; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.ai_segmentations (id, patient_id, doctor_id, image_series_id, status, input_parameters, segmentation_results, volume_analysis, tumor_classification, confidence_score, processing_time, preprocessing_params, postprocessing_params, started_at, completed_at, validated_at) FROM stdin;
5d581da8-605f-4d0e-a6f4-bbb437b1ed8b	35c24a7d-e816-4277-94d0-ada189d983c5	\N	e7fb2c3a-7ea7-48bb-9943-5add4c2362a9	FAILED	{"modalities_used": ["FLAIR", "T2", "T1", "T1CE"], "model_version": "U-Net Kaggle v2.1", "processing_mode": "real", "patient_id": "35c24a7d-e816-4277-94d0-ada189d983c5", "image_count": 4}	\N	\N	\N	\N	\N	\N	\N	2025-06-01 11:04:37.884921	2025-06-01 11:04:40.300416	\N
47c873b4-f0af-4cc8-83c0-14f2708ee613	35c24a7d-e816-4277-94d0-ada189d983c5	\N	365aa461-d1c9-401c-a36d-767498008fc4	PROCESSING	{"modalities_used": ["T2", "T1CE", "T1", "FLAIR"], "model_version": "U-Net Kaggle v2.1", "processing_mode": "real", "patient_id": "35c24a7d-e816-4277-94d0-ada189d983c5", "image_count": 4}	\N	\N	\N	\N	\N	\N	\N	2025-06-01 11:07:45.788551	\N	\N
95882e1c-48cd-486d-b1ab-12d6243e52f7	35c24a7d-e816-4277-94d0-ada189d983c5	\N	0eccb2a4-d9cd-4d69-8ec1-3b1930633f2d	PROCESSING	{"modalities_used": ["FLAIR", "T1CE", "T2", "T1"], "model_version": "U-Net Kaggle v2.1", "processing_mode": "real", "patient_id": "35c24a7d-e816-4277-94d0-ada189d983c5", "image_count": 4}	\N	\N	\N	\N	\N	\N	\N	2025-06-01 11:09:48.811728	\N	\N
3bde023f-591c-407a-a0ef-4d8e6f314301	35c24a7d-e816-4277-94d0-ada189d983c5	\N	823d3fdf-07aa-4fb0-a248-114ff916a95c	COMPLETED	{"modalities_used": ["T2", "T1CE", "FLAIR", "T1"], "model_version": "U-Net Kaggle v2.1", "processing_mode": "real", "patient_id": "35c24a7d-e816-4277-94d0-ada189d983c5", "image_count": 4}	{"total_tumor_volume_cm3": 41.121, "tumor_analysis": {"total_volume_cm3": 41.121, "tumor_segments": [{"type": "NECROTIC_CORE", "name": "Noyau n\\u00e9crotique/kystique", "volume_cm3": 0.0, "percentage": 0.0, "color_code": "#FF0000", "confidence": 0.85, "description": "Zone centrale n\\u00e9crotique"}, {"type": "PERITUMORAL_EDEMA", "name": "\\u0152d\\u00e8me p\\u00e9ritumoral", "volume_cm3": 0.0, "percentage": 0.0, "color_code": "#00FF00", "confidence": 0.85, "description": "\\u0152d\\u00e8me autour de la tumeur"}, {"type": "ENHANCING_TUMOR", "name": "Tumeur rehauss\\u00e9e", "volume_cm3": 0.0, "percentage": 0.0, "color_code": "#0080FF", "confidence": 0.85, "description": "Tumeur active avec prise de contraste"}]}, "clinical_metrics": {"dice_coefficient": 0.85, "precision": 0.82, "sensitivity": 0.88, "specificity": 0.91}, "recommendations": ["Volume tumoral total: 41.12 cm\\u00b3", "Corr\\u00e9lation avec l'expertise du radiologue recommand\\u00e9e", "Suivi volum\\u00e9trique recommand\\u00e9 dans 3 mois"]}	{"total_volume_cm3": 41.121, "tumor_segments": [{"type": "NECROTIC_CORE", "name": "Noyau n\\u00e9crotique/kystique", "volume_cm3": 0.0, "percentage": 0.0, "color_code": "#FF0000", "confidence": 0.85, "description": "Zone centrale n\\u00e9crotique"}, {"type": "PERITUMORAL_EDEMA", "name": "\\u0152d\\u00e8me p\\u00e9ritumoral", "volume_cm3": 0.0, "percentage": 0.0, "color_code": "#00FF00", "confidence": 0.85, "description": "\\u0152d\\u00e8me autour de la tumeur"}, {"type": "ENHANCING_TUMOR", "name": "Tumeur rehauss\\u00e9e", "volume_cm3": 0.0, "percentage": 0.0, "color_code": "#0080FF", "confidence": 0.85, "description": "Tumeur active avec prise de contraste"}], "modalities_used": ["t1", "t1ce", "t2", "flair"], "representative_slices": [50, 75, 99]}	\N	0.8700	2-5 minutes	\N	\N	2025-06-01 11:13:19.360647	2025-06-01 11:13:48.442495	\N
8a8f8f4d-9435-40a3-ad3c-867c5bb75747	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	\N	d44e2b35-88e7-4380-b1ed-ec57a8f221e5	VALIDATED	{"modalities_used": ["T2", "FLAIR", "T1CE", "T1"], "model_version": "U-Net Kaggle v2.1", "processing_mode": "real", "patient_id": "2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15", "image_count": 4}	{"total_tumor_volume_cm3": 35.533, "tumor_analysis": {"total_volume_cm3": 35.533, "tumor_segments": [{"type": "NECROTIC_CORE", "name": "Noyau n\\u00e9crotique/kystique", "volume_cm3": 6.165, "percentage": 17.35006894999015, "color_code": "#FF0000", "description": "Zone centrale n\\u00e9crotique"}, {"type": "PERITUMORAL_EDEMA", "name": "\\u0152d\\u00e8me p\\u00e9ritumoral", "volume_cm3": 12.561, "percentage": 35.35023780710888, "color_code": "#00FF00", "description": "\\u0152d\\u00e8me autour de la tumeur"}, {"type": "ENHANCING_TUMOR", "name": "Tumeur rehauss\\u00e9e", "volume_cm3": 16.807, "percentage": 47.29969324290096, "color_code": "#0080FF", "description": "Tumeur active avec prise de contraste"}]}, "recommendations": ["Volume tumoral total: 35.53 cm\\u00b3", "Corr\\u00e9lation avec l'expertise du radiologue recommand\\u00e9e", "Suivi volum\\u00e9trique recommand\\u00e9 dans 3 mois"]}	{"total_volume_cm3": 35.533, "tumor_segments": [{"type": "NECROTIC_CORE", "name": "Noyau n\\u00e9crotique/kystique", "volume_cm3": 6.165, "percentage": 17.35006894999015, "color_code": "#FF0000", "description": "Zone centrale n\\u00e9crotique"}, {"type": "PERITUMORAL_EDEMA", "name": "\\u0152d\\u00e8me p\\u00e9ritumoral", "volume_cm3": 12.561, "percentage": 35.35023780710888, "color_code": "#00FF00", "description": "\\u0152d\\u00e8me autour de la tumeur"}, {"type": "ENHANCING_TUMOR", "name": "Tumeur rehauss\\u00e9e", "volume_cm3": 16.807, "percentage": 47.29969324290096, "color_code": "#0080FF", "description": "Tumeur active avec prise de contraste"}], "modalities_used": ["t1", "t1ce", "t2", "flair"], "representative_slices": [56, 74, 92]}	\N	0.8700	2-5 minutes	\N	\N	2025-06-01 13:45:25.290278	2025-06-01 13:46:00.692646	2025-06-01 13:16:10.386018
4a22e55d-d70e-42a2-8cdc-adedacdfd2cf	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	d12b0098-46d5-4277-9a13-0893e68779c1	3b29281d-38e1-4dae-80d0-b835e9448e98	VALIDATED	{"modalities_used": ["FLAIR", "T1CE", "T1", "T2"], "model_version": "U-Net Kaggle v2.1", "processing_mode": "real", "patient_id": "2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15", "image_count": 4}	{"total_tumor_volume_cm3": 35.533, "tumor_analysis": {"total_volume_cm3": 35.533, "tumor_segments": [{"type": "NECROTIC_CORE", "name": "Noyau n\\u00e9crotique/kystique", "volume_cm3": 6.165, "percentage": 17.35006894999015, "color_code": "#FF0000", "description": "Zone centrale n\\u00e9crotique"}, {"type": "PERITUMORAL_EDEMA", "name": "\\u0152d\\u00e8me p\\u00e9ritumoral", "volume_cm3": 12.561, "percentage": 35.35023780710888, "color_code": "#00FF00", "description": "\\u0152d\\u00e8me autour de la tumeur"}, {"type": "ENHANCING_TUMOR", "name": "Tumeur rehauss\\u00e9e", "volume_cm3": 16.807, "percentage": 47.29969324290096, "color_code": "#0080FF", "description": "Tumeur active avec prise de contraste"}]}, "recommendations": ["Volume tumoral total: 35.53 cm\\u00b3", "Corr\\u00e9lation avec l'expertise du radiologue recommand\\u00e9e", "Suivi volum\\u00e9trique recommand\\u00e9 dans 3 mois"]}	{"total_volume_cm3": 35.533, "tumor_segments": [{"type": "NECROTIC_CORE", "name": "Noyau n\\u00e9crotique/kystique", "volume_cm3": 6.165, "percentage": 17.35006894999015, "color_code": "#FF0000", "description": "Zone centrale n\\u00e9crotique"}, {"type": "PERITUMORAL_EDEMA", "name": "\\u0152d\\u00e8me p\\u00e9ritumoral", "volume_cm3": 12.561, "percentage": 35.35023780710888, "color_code": "#00FF00", "description": "\\u0152d\\u00e8me autour de la tumeur"}, {"type": "ENHANCING_TUMOR", "name": "Tumeur rehauss\\u00e9e", "volume_cm3": 16.807, "percentage": 47.29969324290096, "color_code": "#0080FF", "description": "Tumeur active avec prise de contraste"}], "modalities_used": ["t1", "t1ce", "t2", "flair"], "representative_slices": [56, 74, 92]}	\N	0.8700	2-5 minutes	\N	\N	2025-06-01 14:24:01.871342	2025-06-01 14:24:49.592633	2025-06-01 13:27:24.979007
06d989bf-4cc8-4bc6-9199-450888978f36	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	daaf3671-19e4-4a6d-9b89-27867671b416	COMPLETED	{"modalities_used": ["T2", "FLAIR", "T1CE", "T1"], "model_version": "U-Net Kaggle v2.1", "processing_mode": "real", "patient_id": "04813c40-0621-4aae-ae7c-e8e7cb0539c3", "image_count": 4}	{"total_tumor_volume_cm3": 41.121, "tumor_analysis": {"total_volume_cm3": 41.121, "tumor_segments": [{"type": "NECROTIC_CORE", "name": "Noyau n\\u00e9crotique/kystique", "volume_cm3": 7.326, "percentage": 17.81571459838039, "color_code": "#FF0000", "description": "Zone centrale n\\u00e9crotique"}, {"type": "PERITUMORAL_EDEMA", "name": "\\u0152d\\u00e8me p\\u00e9ritumoral", "volume_cm3": 20.675, "percentage": 50.278446535833275, "color_code": "#00FF00", "description": "\\u0152d\\u00e8me autour de la tumeur"}, {"type": "ENHANCING_TUMOR", "name": "Tumeur rehauss\\u00e9e", "volume_cm3": 13.12, "percentage": 31.905838865786336, "color_code": "#0080FF", "description": "Tumeur active avec prise de contraste"}]}, "recommendations": ["Volume tumoral total: 41.12 cm\\u00b3", "Corr\\u00e9lation avec l'expertise du radiologue recommand\\u00e9e", "Suivi volum\\u00e9trique recommand\\u00e9 dans 3 mois"]}	{"total_volume_cm3": 41.121, "tumor_segments": [{"type": "NECROTIC_CORE", "name": "Noyau n\\u00e9crotique/kystique", "volume_cm3": 7.326, "percentage": 17.81571459838039, "color_code": "#FF0000", "description": "Zone centrale n\\u00e9crotique"}, {"type": "PERITUMORAL_EDEMA", "name": "\\u0152d\\u00e8me p\\u00e9ritumoral", "volume_cm3": 20.675, "percentage": 50.278446535833275, "color_code": "#00FF00", "description": "\\u0152d\\u00e8me autour de la tumeur"}, {"type": "ENHANCING_TUMOR", "name": "Tumeur rehauss\\u00e9e", "volume_cm3": 13.12, "percentage": 31.905838865786336, "color_code": "#0080FF", "description": "Tumeur active avec prise de contraste"}], "modalities_used": ["t1", "t1ce", "t2", "flair"], "representative_slices": [50, 75, 99]}	\N	0.8700	2-5 minutes	\N	\N	2025-06-01 22:08:13.649332	2025-06-01 22:09:04.985038	\N
fb1bf765-8538-43be-a3af-51489b85f04c	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	5622167b-6cc4-4899-acc6-10accf1aa2b0	VALIDATED	{"modalities_used": ["T2", "FLAIR", "T1", "T1CE"], "model_version": "U-Net Kaggle v2.1", "processing_mode": "real", "patient_id": "04813c40-0621-4aae-ae7c-e8e7cb0539c3", "image_count": 8}	{"total_tumor_volume_cm3": 35.533, "tumor_analysis": {"total_volume_cm3": 35.533, "tumor_segments": [{"type": "NECROTIC_CORE", "name": "Noyau n\\u00e9crotique/kystique", "volume_cm3": 6.165, "percentage": 17.35006894999015, "color_code": "#FF0000", "description": "Zone centrale n\\u00e9crotique"}, {"type": "PERITUMORAL_EDEMA", "name": "\\u0152d\\u00e8me p\\u00e9ritumoral", "volume_cm3": 12.561, "percentage": 35.35023780710888, "color_code": "#00FF00", "description": "\\u0152d\\u00e8me autour de la tumeur"}, {"type": "ENHANCING_TUMOR", "name": "Tumeur rehauss\\u00e9e", "volume_cm3": 16.807, "percentage": 47.29969324290096, "color_code": "#0080FF", "description": "Tumeur active avec prise de contraste"}]}, "recommendations": ["Volume tumoral total: 35.53 cm\\u00b3", "Corr\\u00e9lation avec l'expertise du radiologue recommand\\u00e9e", "Suivi volum\\u00e9trique recommand\\u00e9 dans 3 mois"]}	{"total_volume_cm3": 35.533, "tumor_segments": [{"type": "NECROTIC_CORE", "name": "Noyau n\\u00e9crotique/kystique", "volume_cm3": 6.165, "percentage": 17.35006894999015, "color_code": "#FF0000", "description": "Zone centrale n\\u00e9crotique"}, {"type": "PERITUMORAL_EDEMA", "name": "\\u0152d\\u00e8me p\\u00e9ritumoral", "volume_cm3": 12.561, "percentage": 35.35023780710888, "color_code": "#00FF00", "description": "\\u0152d\\u00e8me autour de la tumeur"}, {"type": "ENHANCING_TUMOR", "name": "Tumeur rehauss\\u00e9e", "volume_cm3": 16.807, "percentage": 47.29969324290096, "color_code": "#0080FF", "description": "Tumeur active avec prise de contraste"}], "modalities_used": ["t1", "t1ce", "t2", "flair", "t1", "t1ce", "t2", "flair"], "representative_slices": [56, 74, 92]}	\N	0.8700	2-5 minutes	\N	\N	2025-06-02 02:15:25.54851	2025-06-02 02:16:21.570449	2025-06-02 02:29:46.535929
\.


--
-- Data for Name: appointment_reminders; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.appointment_reminders (id, appointment_id, reminder_type, recipient_contact, scheduled_time, is_sent, sent_at, retry_count, created_at) FROM stdin;
\.


--
-- Data for Name: appointments; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.appointments (id, patient_id, doctor_id, scheduled_by_user_id, appointment_date, appointment_time, status, notes, previous_appointment_id, appointment_type, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: doctors; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.doctors (id, user_id, bio, office_location, is_active, created_at, updated_at) FROM stdin;
9b8934ba-470b-4f39-843b-f407d0f7b1c7	92ba5caa-db13-46ae-a9c1-fd43238fcbad	bio	x	t	2025-05-30 19:12:56.19302	2025-05-30 19:12:56.19302
c1da3881-82b1-4efe-b3c2-1ba66f10f03f	8f48efcd-9129-4da4-bfb8-c3d0cd20b25c	bio	a	t	2025-05-30 19:18:25.788329	2025-05-30 19:18:25.788329
d12b0098-46d5-4277-9a13-0893e68779c1	823903c2-75b0-48d1-bc7e-499f10e4c3a1	bio	chera3 l mo3ez nahj l asfar	t	2025-06-01 14:12:37.643732	2025-06-01 14:12:37.643732
e0c49433-bfaa-4d80-ae11-08ce6f6ce588	a47bdb6a-291d-4d5e-bc37-a35104c0a70d	Neurochirurgien spécialisé en tumeurs cérébrales	Bureau 201, Aile Neurologie	t	2025-06-01 16:24:37.767061	2025-06-01 16:24:37.767061
\.


--
-- Data for Name: image_series; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.image_series (id, patient_id, series_name, description, image_ids, acquisition_date, technical_parameters, study_instance_uid, series_instance_uid, slice_count, created_at) FROM stdin;
c64927e9-dfc3-4075-b7fe-19471991c9a1	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 01:54	Série d'images pour segmentation IA - Modalités: T1CE, FLAIR, T1, T2	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["T1CE", "FLAIR", "T1", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 01:54:33.604778
8dba2d93-906f-4b2c-aa5c-48139ad33923	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 01:55	Série d'images pour segmentation IA - Modalités: T1CE, FLAIR, T1, T2	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["T1CE", "FLAIR", "T1", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 01:55:21.536029
60187cd2-59bd-41ad-b07e-5b71138b4c3f	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 01:55	Série d'images pour segmentation IA - Modalités: T1CE, FLAIR, T1, T2	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["T1CE", "FLAIR", "T1", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 01:55:38.523687
23aec9ea-9aae-4c55-817a-6cd78fa02dde	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 01:56	Série d'images pour segmentation IA - Modalités: T1CE, FLAIR, T1, T2	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["T1CE", "FLAIR", "T1", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 01:56:04.65637
ea35c2ec-3acc-4d4e-acb0-5b02a8198795	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:03	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1, T1CE	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["FLAIR", "T2", "T1", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:03:10.853084
dba8045a-5da6-4ab3-91ea-6bdb9c835e49	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:03	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1, T1CE	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["FLAIR", "T2", "T1", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:03:53.47476
d9451c2c-da6e-4304-a646-820cff919bd2	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:05	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1, T1CE	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["FLAIR", "T2", "T1", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:05:17.494073
961ab753-e302-4246-b556-44729f0540af	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:05	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1, T1CE	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["FLAIR", "T2", "T1", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:05:46.825837
10fcbb7f-ce9e-4ca2-ac49-2d82ae3739f5	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:11	Série d'images pour segmentation IA - Modalités: T2, FLAIR, T1CE, T1	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["T2", "FLAIR", "T1CE", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:11:46.695999
325330bd-2e04-4c4e-ae9c-47638ad5b1ef	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:22	Série d'images pour segmentation IA - Modalités: FLAIR, T1CE, T2, T1	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["FLAIR", "T1CE", "T2", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:22:13.123202
cf94d94b-c02f-4e2b-aeb3-cf1ec39845a2	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:25	Série d'images pour segmentation IA - Modalités: T1, T2, FLAIR, T1CE	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["T1", "T2", "FLAIR", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:25:50.231949
cae8f077-00b7-4f53-b163-13c1285bf38b	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:31	Série d'images pour segmentation IA - Modalités: T2, T1CE, FLAIR, T1	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["T2", "T1CE", "FLAIR", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:31:12.786046
ea063fc2-c8bc-4bc0-8279-43f885ee9fd3	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:31	Série d'images pour segmentation IA - Modalités: T2, T1CE, FLAIR, T1	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["T2", "T1CE", "FLAIR", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:31:38.187834
2d7d43e7-03b1-47e3-ba99-641aa2fa1f51	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:42	Série d'images pour segmentation IA - Modalités: FLAIR, T1, T1CE, T2	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["FLAIR", "T1", "T1CE", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:42:10.077308
e33e89ba-91fc-4a11-9814-1a40dd85d514	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 02:47	Série d'images pour segmentation IA - Modalités: FLAIR, T1, T1CE, T2	["f8ea55e4-52a4-4328-b0b2-6d368610b75f", "d68a3470-b865-4791-8823-cb044b51fae2", "9255a740-a95c-4575-b883-99ea7f2d2bcf", "90deb93c-8c54-4326-bb85-7d72ae688ef0"]	2025-05-30	{"modalities": ["FLAIR", "T1", "T1CE", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 02:47:41.682963
4d9b0e04-aa2e-4f23-8f40-8b0a4327868f	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 04:00	Série d'images pour segmentation IA - Modalités: T2, FLAIR, T1CE, T1	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T2", "FLAIR", "T1CE", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 04:00:55.957274
f985667f-8a3c-4959-94d0-eff476f2087f	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 04:07	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1, T1CE	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T2", "T1", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 04:07:21.452123
b67cd7b8-e1ef-4dce-b5dd-e555515b5aef	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 04:10	Série d'images pour segmentation IA - Modalités: T1, T2, T1CE, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1", "T2", "T1CE", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 04:10:56.052317
16922853-0734-4aa2-bdd8-700eea79689f	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 04:12	Série d'images pour segmentation IA - Modalités: T1, T2, T1CE, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1", "T2", "T1CE", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 04:12:22.002185
48cc1224-3815-49b8-ba9f-b2bec1fab994	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 04:15	Série d'images pour segmentation IA - Modalités: T1CE, T1, FLAIR, T2	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1CE", "T1", "FLAIR", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 04:15:25.80787
a6a12c24-b514-4369-b3ef-9c9169e9c999	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 04:17	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1, T1CE	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T2", "T1", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 04:17:39.278062
e842c9d1-a7fe-49fe-8748-0190f6c52df1	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 04:19	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1, T1CE	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T2", "T1", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 04:19:03.875798
6680ae6d-fe72-405b-a543-88a22eee3860	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 04:23	Série d'images pour segmentation IA - Modalités: T1, FLAIR, T1CE, T2	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1", "FLAIR", "T1CE", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 04:23:24.661872
41c75cea-8974-4738-a35a-e971d147bb8e	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 04:46	Série d'images pour segmentation IA - Modalités: T2, T1, T1CE, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T2", "T1", "T1CE", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 04:46:27.890317
a9bd6b54-64d7-4b5b-b230-d43f2c98392a	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 17:39	Série d'images pour segmentation IA - Modalités: FLAIR, T1, T1CE, T2	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T1", "T1CE", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 17:39:58.502908
52d50c22-208d-4ec8-aeeb-98c04cb8ece3	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 17:40	Série d'images pour segmentation IA - Modalités: FLAIR, T1, T1CE, T2	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T1", "T1CE", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 17:40:56.497924
3eb7f591-77d4-4b7a-8823-9d62f9335c64	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 17:41	Série d'images pour segmentation IA - Modalités: FLAIR, T1, T1CE, T2	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T1", "T1CE", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 17:41:22.232762
377af635-de20-4b7c-9593-032fbc59230b	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 17:44	Série d'images pour segmentation IA - Modalités: FLAIR, T1, T2, T1CE	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T1", "T2", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 17:44:55.551116
9854d63d-2929-46e4-be10-f2ecfad400fc	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 17:56	Série d'images pour segmentation IA - Modalités: FLAIR, T1CE, T1, T2	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T1CE", "T1", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 17:56:46.898521
bc7f6de6-a96b-424b-adda-d9a4b0751bc4	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 18:03	Série d'images pour segmentation IA - Modalités: T1CE, T1, T2, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1CE", "T1", "T2", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 18:03:45.9466
745a5260-a492-4d70-a1b5-1f907b1e430f	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 18:05	Série d'images pour segmentation IA - Modalités: T1CE, T1, T2, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1CE", "T1", "T2", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 18:05:25.682169
a9646481-7add-4ce3-8162-7b4cfacb970d	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 18:12	Série d'images pour segmentation IA - Modalités: FLAIR, T1CE, T2, T1	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T1CE", "T2", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 18:12:55.256654
d8da4824-8339-46da-80c5-df5f4a42888f	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 18:23	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1CE, T1	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T2", "T1CE", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 18:23:00.424917
2404dda4-d8c3-406c-a0a5-4f47d60c8d3b	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 18:24	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1CE, T1	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T2", "T1CE", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 18:24:54.643012
1830dbf9-6939-46f9-86f8-7c6082e54eaf	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 18:38	Série d'images pour segmentation IA - Modalités: T1, T1CE, T2, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1", "T1CE", "T2", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 18:38:21.364547
96172a0e-3c38-4122-a717-8d3c76f27098	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 18:56	Série d'images pour segmentation IA - Modalités: T1CE, T2, T1, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1CE", "T2", "T1", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 18:56:33.181995
af0773b3-bec3-4895-9a9a-161b41543f54	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 18:58	Série d'images pour segmentation IA - Modalités: T1CE, T1, T2, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1CE", "T1", "T2", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 18:58:50.16004
3d6bec5c-3518-4bc7-8583-ae4b6978ceef	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 19:03	Série d'images pour segmentation IA - Modalités: T2, T1CE, T1, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T2", "T1CE", "T1", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 19:03:57.501044
9b58eb24-1e9a-4e60-9fb6-3f2fa3ef20cf	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 19:11	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1, T1CE	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["FLAIR", "T2", "T1", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 19:11:10.253505
1968c6d6-f572-424f-93ec-2db598bd8209	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 19:39	Série d'images pour segmentation IA - Modalités: T1, FLAIR, T2, T1CE	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1", "FLAIR", "T2", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 19:39:40.884133
23940551-3801-455c-a2d5-de25a8304638	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 22:13	Série d'images pour segmentation IA - Modalités: T1, T2, T1CE, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1", "T2", "T1CE", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 22:13:58.217884
21439543-c94f-47cb-9aa1-181ae5f9329e	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 22:17	Série d'images pour segmentation IA - Modalités: T2, FLAIR, T1CE, T1	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T2", "FLAIR", "T1CE", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 22:17:28.358205
b09fc34b-549f-46a2-8e78-34a20dfa3010	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 22:20	Série d'images pour segmentation IA - Modalités: T1, FLAIR, T1CE, T2	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1", "FLAIR", "T1CE", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 22:20:42.959277
792ab986-3ce7-40dd-b189-ede92ef9abe5	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-05-31 22:24	Série d'images pour segmentation IA - Modalités: T1CE, T1, T2, FLAIR	["9cfb1459-5265-4860-b32c-99f12fb4e016", "5797e172-70ae-4765-b6f3-0e498ff6f6a2", "4eb6913f-306b-4997-83b7-6ec7485ee73a", "2d178602-5f3f-4b49-9e09-24e7ab0e3d9d"]	2025-05-31	{"modalities": ["T1CE", "T1", "T2", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-05-31 22:24:49.334163
e7fb2c3a-7ea7-48bb-9943-5add4c2362a9	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-06-01 11:04	Série d'images pour segmentation IA - Modalités: FLAIR, T2, T1, T1CE	["54412020-1592-4f32-966d-79a1b579ff38", "e5af75fe-09c4-4a68-82ce-465f6dc8998e", "419182d2-5f81-463a-9e2f-eb51d85a59fb", "718e6482-6f53-42d6-a88c-f03d2d3c429d"]	2025-06-01	{"modalities": ["FLAIR", "T2", "T1", "T1CE"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 11:04:37.867865
365aa461-d1c9-401c-a36d-767498008fc4	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-06-01 11:07	Série d'images pour segmentation IA - Modalités: T2, T1CE, T1, FLAIR	["54412020-1592-4f32-966d-79a1b579ff38", "e5af75fe-09c4-4a68-82ce-465f6dc8998e", "419182d2-5f81-463a-9e2f-eb51d85a59fb", "718e6482-6f53-42d6-a88c-f03d2d3c429d"]	2025-06-01	{"modalities": ["T2", "T1CE", "T1", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 11:07:45.713111
0eccb2a4-d9cd-4d69-8ec1-3b1930633f2d	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-06-01 11:09	Série d'images pour segmentation IA - Modalités: FLAIR, T1CE, T2, T1	["54412020-1592-4f32-966d-79a1b579ff38", "e5af75fe-09c4-4a68-82ce-465f6dc8998e", "419182d2-5f81-463a-9e2f-eb51d85a59fb", "718e6482-6f53-42d6-a88c-f03d2d3c429d"]	2025-06-01	{"modalities": ["FLAIR", "T1CE", "T2", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 11:09:48.771404
7f06074f-6d3e-430d-95f2-198fbe52e240	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	Segmentation Series 2025-06-01 11:10	Série d'images pour segmentation IA - Modalités: FLAIR, T1CE, T2, T1	["bfefba7f-85d5-44cf-a2a2-40efca3ee5de", "a0ea041e-1789-4555-94c0-5166dd3f0695", "4148b7b8-5c7b-4785-bfc7-1960daa0c623", "8af13b2b-590a-47dc-a077-f7cdc168cee4"]	2025-06-01	{"modalities": ["FLAIR", "T1CE", "T2", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 11:10:56.856118
823d3fdf-07aa-4fb0-a248-114ff916a95c	35c24a7d-e816-4277-94d0-ada189d983c5	Segmentation Series 2025-06-01 11:13	Série d'images pour segmentation IA - Modalités: T2, T1CE, FLAIR, T1	["54412020-1592-4f32-966d-79a1b579ff38", "e5af75fe-09c4-4a68-82ce-465f6dc8998e", "419182d2-5f81-463a-9e2f-eb51d85a59fb", "718e6482-6f53-42d6-a88c-f03d2d3c429d"]	2025-06-01	{"modalities": ["T2", "T1CE", "FLAIR", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 11:13:19.317758
903927cb-726d-4b55-a4f3-30e79a8c3b9b	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	Segmentation Series 2025-06-01 11:14	Série d'images pour segmentation IA - Modalités: T2, T1CE, FLAIR, T1	["bfefba7f-85d5-44cf-a2a2-40efca3ee5de", "a0ea041e-1789-4555-94c0-5166dd3f0695", "4148b7b8-5c7b-4785-bfc7-1960daa0c623", "8af13b2b-590a-47dc-a077-f7cdc168cee4"]	2025-06-01	{"modalities": ["T2", "T1CE", "FLAIR", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 11:14:41.955874
e3703aea-7d44-4bc9-aea6-bb6c1ab52eac	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	Segmentation Series 2025-06-01 11:21	Série d'images pour segmentation IA - Modalités: T1CE, T2, T1, FLAIR	["bfefba7f-85d5-44cf-a2a2-40efca3ee5de", "a0ea041e-1789-4555-94c0-5166dd3f0695", "4148b7b8-5c7b-4785-bfc7-1960daa0c623", "8af13b2b-590a-47dc-a077-f7cdc168cee4"]	2025-06-01	{"modalities": ["T1CE", "T2", "T1", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 11:21:40.092173
0b2ebf2b-3d32-4ec8-9f38-0a3470eed09d	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	Segmentation Series 2025-06-01 11:22	Série d'images pour segmentation IA - Modalités: T1CE, T2, T1, FLAIR	["bfefba7f-85d5-44cf-a2a2-40efca3ee5de", "a0ea041e-1789-4555-94c0-5166dd3f0695", "4148b7b8-5c7b-4785-bfc7-1960daa0c623", "8af13b2b-590a-47dc-a077-f7cdc168cee4"]	2025-06-01	{"modalities": ["T1CE", "T2", "T1", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 11:22:24.315245
168d932a-c2b5-4dce-b23d-9b0598b20c38	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	Segmentation Series 2025-06-01 11:35	Série d'images pour segmentation IA - Modalités: T1CE, T2, T1, FLAIR	["bfefba7f-85d5-44cf-a2a2-40efca3ee5de", "a0ea041e-1789-4555-94c0-5166dd3f0695", "4148b7b8-5c7b-4785-bfc7-1960daa0c623", "8af13b2b-590a-47dc-a077-f7cdc168cee4"]	2025-06-01	{"modalities": ["T1CE", "T2", "T1", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 11:35:11.44555
d44e2b35-88e7-4380-b1ed-ec57a8f221e5	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	Segmentation Series 2025-06-01 13:45	Série d'images pour segmentation IA - Modalités: T2, FLAIR, T1CE, T1	["bfefba7f-85d5-44cf-a2a2-40efca3ee5de", "a0ea041e-1789-4555-94c0-5166dd3f0695", "4148b7b8-5c7b-4785-bfc7-1960daa0c623", "8af13b2b-590a-47dc-a077-f7cdc168cee4"]	2025-06-01	{"modalities": ["T2", "FLAIR", "T1CE", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 13:45:25.2764
3b29281d-38e1-4dae-80d0-b835e9448e98	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	Segmentation Series 2025-06-01 14:24	Série d'images pour segmentation IA - Modalités: FLAIR, T1CE, T1, T2	["bfefba7f-85d5-44cf-a2a2-40efca3ee5de", "a0ea041e-1789-4555-94c0-5166dd3f0695", "4148b7b8-5c7b-4785-bfc7-1960daa0c623", "8af13b2b-590a-47dc-a077-f7cdc168cee4"]	2025-06-01	{"modalities": ["FLAIR", "T1CE", "T1", "T2"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 14:24:01.842958
93d15f8e-76b7-400d-a93a-8c601f82fb1a	04813c40-0621-4aae-ae7c-e8e7cb0539c3	Segmentation Series 2025-06-01 18:09	Série d'images pour segmentation IA - Modalités: T1CE, T1, T2, FLAIR	["52e0e7fd-86e2-4b19-93cb-ea8bfe3bda9b", "381bb034-ca61-4c0b-aa88-e50c558fd505", "34ea9b33-7b8a-43ee-a537-254f01f7de3f", "e15332c5-ab7a-4a0e-b6a4-e7178653ba33"]	2025-06-01	{"modalities": ["T1CE", "T1", "T2", "FLAIR"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 18:09:23.531948
d6f02338-32c6-42ce-8ef1-41830b92898b	04813c40-0621-4aae-ae7c-e8e7cb0539c3	Segmentation Series 2025-06-01 18:44	Série d'images pour segmentation IA - Modalités: T1CE, T1, T2, FLAIR	["52e0e7fd-86e2-4b19-93cb-ea8bfe3bda9b", "381bb034-ca61-4c0b-aa88-e50c558fd505", "34ea9b33-7b8a-43ee-a537-254f01f7de3f", "e15332c5-ab7a-4a0e-b6a4-e7178653ba33", "3aea76f9-5918-40d6-9b63-3f6b4cd7f676", "af71b302-41e1-4f0d-b408-6c72e236f813", "4c455aad-1354-4612-bc2e-33b0ed675ca7", "82f3ccda-ca20-4ed7-b290-8bac996f0ae6"]	2025-06-01	{"modalities": ["T1CE", "T1", "T2", "FLAIR"], "total_images": 8, "created_for_segmentation": true}	\N	\N	8	2025-06-01 18:44:53.191787
daaf3671-19e4-4a6d-9b89-27867671b416	04813c40-0621-4aae-ae7c-e8e7cb0539c3	Segmentation Series 2025-06-01 22:08	Série d'images pour segmentation IA - Modalités: T2, FLAIR, T1CE, T1	["3aea76f9-5918-40d6-9b63-3f6b4cd7f676", "af71b302-41e1-4f0d-b408-6c72e236f813", "4c455aad-1354-4612-bc2e-33b0ed675ca7", "82f3ccda-ca20-4ed7-b290-8bac996f0ae6"]	2025-06-07	{"modalities": ["T2", "FLAIR", "T1CE", "T1"], "total_images": 4, "created_for_segmentation": true}	\N	\N	4	2025-06-01 22:08:13.646888
5622167b-6cc4-4899-acc6-10accf1aa2b0	04813c40-0621-4aae-ae7c-e8e7cb0539c3	Segmentation Series 2025-06-02 02:15	Série d'images pour segmentation IA - Modalités: T2, FLAIR, T1, T1CE	["3aea76f9-5918-40d6-9b63-3f6b4cd7f676", "af71b302-41e1-4f0d-b408-6c72e236f813", "4c455aad-1354-4612-bc2e-33b0ed675ca7", "82f3ccda-ca20-4ed7-b290-8bac996f0ae6", "bfe4ef8c-5c06-4301-9082-4ac8c38d9790", "ab66cf11-c9c8-4b1a-a283-de73e320ee54", "3a6ad5ad-8059-4c08-afcf-1103aa775bb3", "feb5a483-64d5-46d9-8c07-03fa0f0dd08f"]	2025-06-07	{"modalities": ["T2", "FLAIR", "T1", "T1CE"], "total_images": 8, "created_for_segmentation": true}	\N	\N	8	2025-06-02 02:15:25.510094
\.


--
-- Data for Name: medical_images; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.medical_images (id, patient_id, uploaded_by_user_id, modality, file_path, file_name, file_size, image_metadata, acquisition_date, body_part, notes, is_processed, dicom_metadata, uploaded_at) FROM stdin;
bfefba7f-85d5-44cf-a2a2-40efca3ee5de	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	T1	uploads\\medical_images\\2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15\\9c253c98-32ae-4776-b095-fd86767fec51_t1.nii	9c253c98-32ae-4776-b095-fd86767fec51_t1.nii	35712352	{"series_id": "9c253c98-32ae-4776-b095-fd86767fec51", "original_filename": "BraTS20_Training_355_t1.nii", "content_type": "application/octet-stream"}	2025-06-01	BRAIN	malade	f	\N	2025-06-01 10:43:12.776774
a0ea041e-1789-4555-94c0-5166dd3f0695	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	T1CE	uploads\\medical_images\\2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15\\9c253c98-32ae-4776-b095-fd86767fec51_t1ce.nii	9c253c98-32ae-4776-b095-fd86767fec51_t1ce.nii	35712352	{"series_id": "9c253c98-32ae-4776-b095-fd86767fec51", "original_filename": "BraTS20_Training_355_t1ce.nii", "content_type": "application/octet-stream"}	2025-06-01	BRAIN	malade	f	\N	2025-06-01 10:43:12.920047
4148b7b8-5c7b-4785-bfc7-1960daa0c623	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	T2	uploads\\medical_images\\2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15\\9c253c98-32ae-4776-b095-fd86767fec51_t2.nii	9c253c98-32ae-4776-b095-fd86767fec51_t2.nii	35712352	{"series_id": "9c253c98-32ae-4776-b095-fd86767fec51", "original_filename": "BraTS20_Training_355_t2.nii", "content_type": "application/octet-stream"}	2025-06-01	BRAIN	malade	f	\N	2025-06-01 10:43:13.113915
8af13b2b-590a-47dc-a077-f7cdc168cee4	2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	FLAIR	uploads\\medical_images\\2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15\\9c253c98-32ae-4776-b095-fd86767fec51_flair.nii	9c253c98-32ae-4776-b095-fd86767fec51_flair.nii	35712352	{"series_id": "9c253c98-32ae-4776-b095-fd86767fec51", "original_filename": "BraTS20_Training_355_flair.nii", "content_type": "application/octet-stream"}	2025-06-01	BRAIN	malade	f	\N	2025-06-01 10:43:13.291964
54412020-1592-4f32-966d-79a1b579ff38	35c24a7d-e816-4277-94d0-ada189d983c5	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	T1	uploads\\medical_images\\35c24a7d-e816-4277-94d0-ada189d983c5\\88ca6593-87e3-444d-a87b-05f8844d3cf2_t1.nii	88ca6593-87e3-444d-a87b-05f8844d3cf2_t1.nii	17859216	{"series_id": "88ca6593-87e3-444d-a87b-05f8844d3cf2", "original_filename": "BraTS20_Validation_001_t1.nii", "content_type": "application/octet-stream"}	2025-06-01	BRAIN	mridh	f	\N	2025-06-01 10:46:52.136574
e5af75fe-09c4-4a68-82ce-465f6dc8998e	35c24a7d-e816-4277-94d0-ada189d983c5	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	T1CE	uploads\\medical_images\\35c24a7d-e816-4277-94d0-ada189d983c5\\88ca6593-87e3-444d-a87b-05f8844d3cf2_t1ce.nii	88ca6593-87e3-444d-a87b-05f8844d3cf2_t1ce.nii	17859216	{"series_id": "88ca6593-87e3-444d-a87b-05f8844d3cf2", "original_filename": "BraTS20_Validation_001_t1ce.nii", "content_type": "application/octet-stream"}	2025-06-01	BRAIN	mridh	f	\N	2025-06-01 10:46:52.178682
419182d2-5f81-463a-9e2f-eb51d85a59fb	35c24a7d-e816-4277-94d0-ada189d983c5	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	T2	uploads\\medical_images\\35c24a7d-e816-4277-94d0-ada189d983c5\\88ca6593-87e3-444d-a87b-05f8844d3cf2_t2.nii	88ca6593-87e3-444d-a87b-05f8844d3cf2_t2.nii	17859216	{"series_id": "88ca6593-87e3-444d-a87b-05f8844d3cf2", "original_filename": "BraTS20_Validation_001_t2.nii", "content_type": "application/octet-stream"}	2025-06-01	BRAIN	mridh	f	\N	2025-06-01 10:46:52.227692
718e6482-6f53-42d6-a88c-f03d2d3c429d	35c24a7d-e816-4277-94d0-ada189d983c5	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	FLAIR	uploads\\medical_images\\35c24a7d-e816-4277-94d0-ada189d983c5\\88ca6593-87e3-444d-a87b-05f8844d3cf2_flair.nii	88ca6593-87e3-444d-a87b-05f8844d3cf2_flair.nii	17859216	{"series_id": "88ca6593-87e3-444d-a87b-05f8844d3cf2", "original_filename": "BraTS20_Validation_001_flair.nii", "content_type": "application/octet-stream"}	2025-06-01	BRAIN	mridh	f	\N	2025-06-01 10:46:52.256577
3aea76f9-5918-40d6-9b63-3f6b4cd7f676	04813c40-0621-4aae-ae7c-e8e7cb0539c3	823903c2-75b0-48d1-bc7e-499f10e4c3a1	T1	uploads\\medical_images\\04813c40-0621-4aae-ae7c-e8e7cb0539c3\\62ed7697-761d-4a05-9eee-7b40f007557b_t1.nii	62ed7697-761d-4a05-9eee-7b40f007557b_t1.nii	17859216	{"series_id": "62ed7697-761d-4a05-9eee-7b40f007557b", "original_filename": "BraTS20_Validation_001_t1.nii", "content_type": "application/octet-stream"}	2025-06-07	BRAIN	controle	f	\N	2025-06-01 18:44:08.431644
af71b302-41e1-4f0d-b408-6c72e236f813	04813c40-0621-4aae-ae7c-e8e7cb0539c3	823903c2-75b0-48d1-bc7e-499f10e4c3a1	T1CE	uploads\\medical_images\\04813c40-0621-4aae-ae7c-e8e7cb0539c3\\62ed7697-761d-4a05-9eee-7b40f007557b_t1ce.nii	62ed7697-761d-4a05-9eee-7b40f007557b_t1ce.nii	17859216	{"series_id": "62ed7697-761d-4a05-9eee-7b40f007557b", "original_filename": "BraTS20_Validation_001_t1ce.nii", "content_type": "application/octet-stream"}	2025-06-07	BRAIN	controle	f	\N	2025-06-01 18:44:08.481356
4c455aad-1354-4612-bc2e-33b0ed675ca7	04813c40-0621-4aae-ae7c-e8e7cb0539c3	823903c2-75b0-48d1-bc7e-499f10e4c3a1	T2	uploads\\medical_images\\04813c40-0621-4aae-ae7c-e8e7cb0539c3\\62ed7697-761d-4a05-9eee-7b40f007557b_t2.nii	62ed7697-761d-4a05-9eee-7b40f007557b_t2.nii	17859216	{"series_id": "62ed7697-761d-4a05-9eee-7b40f007557b", "original_filename": "BraTS20_Validation_001_t2.nii", "content_type": "application/octet-stream"}	2025-06-07	BRAIN	controle	f	\N	2025-06-01 18:44:08.517264
82f3ccda-ca20-4ed7-b290-8bac996f0ae6	04813c40-0621-4aae-ae7c-e8e7cb0539c3	823903c2-75b0-48d1-bc7e-499f10e4c3a1	FLAIR	uploads\\medical_images\\04813c40-0621-4aae-ae7c-e8e7cb0539c3\\62ed7697-761d-4a05-9eee-7b40f007557b_flair.nii	62ed7697-761d-4a05-9eee-7b40f007557b_flair.nii	17859216	{"series_id": "62ed7697-761d-4a05-9eee-7b40f007557b", "original_filename": "BraTS20_Validation_001_flair.nii", "content_type": "application/octet-stream"}	2025-06-07	BRAIN	controle	f	\N	2025-06-01 18:44:08.558696
bfe4ef8c-5c06-4301-9082-4ac8c38d9790	04813c40-0621-4aae-ae7c-e8e7cb0539c3	823903c2-75b0-48d1-bc7e-499f10e4c3a1	T1	uploads\\medical_images\\04813c40-0621-4aae-ae7c-e8e7cb0539c3\\f3dc4018-0390-4da4-b668-298f0143c493_t1.nii	f3dc4018-0390-4da4-b668-298f0143c493_t1.nii	35712352	{"series_id": "f3dc4018-0390-4da4-b668-298f0143c493", "original_filename": "BraTS20_Training_355_t1.nii", "content_type": "application/octet-stream"}	2025-06-06	BRAIN	rien	f	\N	2025-06-02 02:15:15.79697
ab66cf11-c9c8-4b1a-a283-de73e320ee54	04813c40-0621-4aae-ae7c-e8e7cb0539c3	823903c2-75b0-48d1-bc7e-499f10e4c3a1	T1CE	uploads\\medical_images\\04813c40-0621-4aae-ae7c-e8e7cb0539c3\\f3dc4018-0390-4da4-b668-298f0143c493_t1ce.nii	f3dc4018-0390-4da4-b668-298f0143c493_t1ce.nii	35712352	{"series_id": "f3dc4018-0390-4da4-b668-298f0143c493", "original_filename": "BraTS20_Training_355_t1ce.nii", "content_type": "application/octet-stream"}	2025-06-06	BRAIN	rien	f	\N	2025-06-02 02:15:16.052732
3a6ad5ad-8059-4c08-afcf-1103aa775bb3	04813c40-0621-4aae-ae7c-e8e7cb0539c3	823903c2-75b0-48d1-bc7e-499f10e4c3a1	T2	uploads\\medical_images\\04813c40-0621-4aae-ae7c-e8e7cb0539c3\\f3dc4018-0390-4da4-b668-298f0143c493_t2.nii	f3dc4018-0390-4da4-b668-298f0143c493_t2.nii	35712352	{"series_id": "f3dc4018-0390-4da4-b668-298f0143c493", "original_filename": "BraTS20_Training_355_t2.nii", "content_type": "application/octet-stream"}	2025-06-06	BRAIN	rien	f	\N	2025-06-02 02:15:16.243152
feb5a483-64d5-46d9-8c07-03fa0f0dd08f	04813c40-0621-4aae-ae7c-e8e7cb0539c3	823903c2-75b0-48d1-bc7e-499f10e4c3a1	FLAIR	uploads\\medical_images\\04813c40-0621-4aae-ae7c-e8e7cb0539c3\\f3dc4018-0390-4da4-b668-298f0143c493_flair.nii	f3dc4018-0390-4da4-b668-298f0143c493_flair.nii	35712352	{"series_id": "f3dc4018-0390-4da4-b668-298f0143c493", "original_filename": "BraTS20_Training_355_flair.nii", "content_type": "application/octet-stream"}	2025-06-06	BRAIN	rien	f	\N	2025-06-02 02:15:16.499831
\.


--
-- Data for Name: medical_records; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.medical_records (id, patient_id, doctor_id, consultation_date, chief_complaint, symptoms, physical_examination, diagnosis, notes, vital_signs, is_final, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: patients; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.patients (id, first_name, last_name, date_of_birth, gender, email, phone, address, blood_type, height, weight, emergency_contact, assigned_doctor_id, created_by_user_id, medical_history, notes, created_at, updated_at) FROM stdin;
35c24a7d-e816-4277-94d0-ada189d983c5	mridh1	mridh	2008-06-30	MALE	mridh@gmail.com	98989898	a	O_NEGATIVE	175	70.00	{"name": "om l mridh", "phone": "99999999", "relationship": "omou"}	\N	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	{"history": "rien", "allergies": "rien", "current_medications": null, "insurance_number": null}	rien	2025-05-30 22:37:24.744062	2025-05-30 23:59:00.106614
2ebcf8d9-69e4-4ba4-a37e-536e7a22ba15	Bruno	Fernandes	2000-05-20	MALE	bruno@gmail.com	95075310	dvsf	O_NEGATIVE	180	65.00	{"name": "Anne Fernandes", "phone": "75757575", "relationship": "Epouse"}	\N	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	{"history": "rien", "allergies": "rien", "current_medications": null, "insurance_number": null}	rien	2025-06-01 10:41:45.514026	2025-06-01 10:41:45.514026
c0ab71b5-a3b1-4440-8fef-ec8aa1a500a4	Amad	Diallo	2001-02-20	MALE	amad@gmail.com	95055555	aa	B_NEGATIVE	190	85.00	{"name": "amada", "phone": "78854123", "relationship": "epouse"}	\N	823903c2-75b0-48d1-bc7e-499f10e4c3a1	{"history": "rien", "allergies": "rien", "current_medications": null, "insurance_number": null}	rien	2025-06-01 17:29:35.495365	2025-06-01 17:29:35.495365
04813c40-0621-4aae-ae7c-e8e7cb0539c3	Matheus	Cunha	1999-03-12	MALE	cunha@gmail.com	99989695	route	A_POSITIVE	185	55.00	{"name": "Cunhae", "phone": "87945321", "relationship": "martou"}	d12b0098-46d5-4277-9a13-0893e68779c1	823903c2-75b0-48d1-bc7e-499f10e4c3a1	{"history": "rien", "allergies": "rien", "current_medications": null, "insurance_number": null}	rien	2025-06-01 17:52:14.919187	2025-06-01 17:52:14.919187
\.


--
-- Data for Name: report_templates; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.report_templates (id, template_name, template_type, content_template, fields_mapping, category, default_values, is_active, created_by_user_id, created_at, updated_at) FROM stdin;
d21e6505-e35e-4882-8cde-1130f71ccf96	Rapport de Segmentation Standard	SEGMENTATION	\n# Rapport de Segmentation - {patient_name}\n\n## Informations Patient\n- **Nom**: {patient_name}\n- **Date de naissance**: {patient_dob}\n- **Date d'examen**: {exam_date}\n\n## Résultats de Segmentation\n- **Volume tumoral total**: {total_volume} cm³\n- **Noyau nécrotique**: {necrotic_volume} cm³ ({necrotic_percentage}%)\n- **Œdème péritumoral**: {edema_volume} cm³ ({edema_percentage}%)\n- **Tumeur rehaussée**: {enhancing_volume} cm³ ({enhancing_percentage}%)\n\n## Score de Confiance\n- **Score global**: {confidence_score}\n\n## Recommandations\n{recommendations}\n\n## Images\n{segmentation_images}\n                	{"patient_name": "patient.first_name + ' ' + patient.last_name", "patient_dob": "patient.date_of_birth", "exam_date": "segmentation.completed_at", "total_volume": "volumetric_analysis.total_tumor_volume", "necrotic_volume": "volumetric_analysis.necrotic_core_volume", "edema_volume": "volumetric_analysis.peritumoral_edema_volume", "enhancing_volume": "volumetric_analysis.enhancing_tumor_volume", "confidence_score": "segmentation.confidence_score"}	MEDICAL	\N	t	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 12:08:51.447518	2025-05-30 12:08:51.447518
7263a434-4f10-47f9-a297-ac5cf7f7e007	Rapport de Consultation Standard	CONSULTATION	\n# Rapport de Consultation - {patient_name}\n\n## Informations Patient\n- **Nom**: {patient_name}\n- **Date de consultation**: {consultation_date}\n- **Médecin**: {doctor_name}\n\n## Motif de consultation\n{chief_complaint}\n\n## Symptômes\n{symptoms}\n\n## Examen physique\n{physical_examination}\n\n## Diagnostic\n{diagnosis}\n\n## Notes\n{notes}\n\n## Plan de traitement\n{treatment_plan}\n                	{"patient_name": "patient.first_name + ' ' + patient.last_name", "consultation_date": "medical_record.consultation_date", "doctor_name": "doctor.user.first_name + ' ' + doctor.user.last_name", "chief_complaint": "medical_record.chief_complaint", "symptoms": "medical_record.symptoms", "physical_examination": "medical_record.physical_examination", "diagnosis": "medical_record.diagnosis", "notes": "medical_record.notes"}	MEDICAL	\N	t	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 12:08:51.447518	2025-05-30 12:08:51.447518
\.


--
-- Data for Name: secretaries; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.secretaries (id, user_id, assigned_doctor_id, department, office_location, phone_extension, responsibilities, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: segmentation_comparisons; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.segmentation_comparisons (id, current_segmentation_id, previous_segmentation_id, volume_changes, morphological_changes, change_percentage, interpretation, statistical_analysis, comparison_date) FROM stdin;
\.


--
-- Data for Name: segmentation_reports; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.segmentation_reports (id, segmentation_id, doctor_id, report_content, findings, recommendations, image_attachments, template_used, quantitative_metrics, is_final, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: treatments; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.treatments (id, patient_id, prescribed_by_doctor_id, treatment_type, medication_name, dosage, frequency, duration, start_date, end_date, status, notes, created_at, updated_at) FROM stdin;
a1bb4fe0-e349-4290-ac35-f5f7ae8f3f98	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	Chimiothérapie	Temozolomide	150 mg/m²	1 fois par jour	6 cycles de 28 jours	2025-05-03	2025-10-30	ACTIVE	Traitement adjuvant post-chirurgie. Surveillance hématologique hebdomadaire.	2025-06-02 04:06:18.414608	2025-06-02 04:06:18.414608
39474c6a-19f1-4b5b-9266-569c056ee4c3	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	Radiothérapie	\N	60 Gy en 30 fractions	5 séances par semaine	6 semaines	2025-02-02	2025-03-16	COMPLETED	Radiothérapie conformationnelle avec modulation d'intensité. Bien tolérée.	2025-02-02 04:06:18.414608	2025-03-16 04:06:18.414608
240f6bf0-84e2-489b-8b2e-3d221cbb1546	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	Traitement symptomatique	Dexaméthasone	4 mg	2 fois par jour	En continu	2025-04-03	\N	ACTIVE	Anti-œdémateux cérébral. Réduction progressive selon tolérance.	2025-04-03 04:06:18.414608	2025-06-02 04:06:18.414608
7ca3ff7d-93a6-4117-b443-244faf670b57	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	Immunothérapie	Bevacizumab	10 mg/kg	Toutes les 2 semaines	12 cycles	2025-03-04	2025-08-01	SUSPENDED	Traitement suspendu temporairement en raison d'effets secondaires (hypertension).	2025-03-04 04:06:18.414608	2025-05-28 04:06:18.414608
814234b8-aadb-455c-a3a3-903b0282f1f3	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	Chirurgie	\N	Résection tumorale complète	Intervention unique	3 heures	2024-12-04	2024-12-04	COMPLETED	Résection tumorale frontale gauche réussie. Récupération post-opératoire normale.	2025-06-02 04:31:02.819707	2025-06-02 04:31:02.819707
2814ed57-41a8-49a5-b4d9-e90f4be0dc7b	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	Radiothérapie	\N	60 Gy en 30 fractions	5 séances par semaine	6 semaines	2025-01-03	2025-02-14	COMPLETED	Radiothérapie conformationnelle post-chirurgicale. Excellente tolérance.	2025-06-02 04:31:02.820099	2025-06-02 04:31:02.820099
032828f2-1b8e-4ee8-bda6-b1604d0cc1f6	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	Chimiothérapie	Temozolomide	150 mg/m²	1 fois par jour, 5 jours/28 jours	6 cycles	2025-03-04	2025-08-01	ACTIVE	Chimiothérapie adjuvante. Cycle 4/6 en cours. Bonne tolérance.	2025-06-02 04:31:02.820099	2025-06-02 04:31:02.820099
a9dfd302-dfe5-471e-86f8-706372eef286	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	Traitement symptomatique	Dexaméthasone	4 mg	2 fois par jour	En continu	2024-12-04	\N	ACTIVE	Anti-œdémateux cérébral. Réduction progressive selon évolution.	2025-06-02 04:31:02.820099	2025-06-02 04:31:02.820099
34b41eea-97ea-424f-8e6a-61fee4b5ab83	04813c40-0621-4aae-ae7c-e8e7cb0539c3	d12b0098-46d5-4277-9a13-0893e68779c1	Traitement symptomatique	Lévétiracétam	500 mg	2 fois par jour	6 mois minimum	2024-12-04	2025-08-31	ACTIVE	Antiépileptique prophylactique post-chirurgie.	2025-06-02 04:31:02.820567	2025-06-02 04:31:02.820567
\.


--
-- Data for Name: tumor_segments; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.tumor_segments (id, segmentation_id, segment_type, volume_cm3, percentage, coordinates, contour_data, color_code, description, confidence_score, statistical_features, created_at) FROM stdin;
\.


--
-- Data for Name: user_credentials; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.user_credentials (user_id, username, password_hash, salt, last_login, failed_login_attempts, is_locked, locked_until, reset_token, token_expires_at) FROM stdin;
823903c2-75b0-48d1-bc7e-499f10e4c3a1	tbib	$2b$12$2W9/LeYssf.aDTjkIqgx9OD1mKZ5H.0CYrMXMHOR8At4DfLOVERv.	$2b$12$2W9/LeYssf.aDTjkIqgx9O	2025-06-02 03:43:39.754158	0	f	\N	\N	\N
92ba5caa-db13-46ae-a9c1-fd43238fcbad	ahmedelmabrouk2000@gmail.com	$2b$12$KhoQkM1F1Nj29R3CHl/k/ugc6UVMUVerNmSv1WZFWq8b.2akt3G6O	$2b$12$KhoQkM1F1Nj29R3CHl/k/u	\N	1	f	\N	\N	\N
8f48efcd-9129-4da4-bfb8-c3d0cd20b25c	ahmedelmabrouk@gmail.com	$2b$12$44BEX26AvOwZrAifViWPteOq97hA9mfswbuHtrq13Kv3nB3wZSZ96	$2b$12$44BEX26AvOwZrAifViWPte	\N	0	f	\N	\N	\N
a47bdb6a-291d-4d5e-bc37-a35104c0a70d	dr.martin	$2b$12$EiJ5Ejdc6YzrOJRFud5bguEWBW66URS5MEFiAjJ6ZNHjGoiHQDPSW	$2b$12$EiJ5Ejdc6YzrOJRFud5bgu	2025-06-01 15:39:04.913275	0	\N	\N	\N	\N
2b0b168e-9502-4a7e-a1e3-78dadeb769e6	admin	$2b$12$ol0ISZXLqII4v4kIavszJeiqvpW.rWvEluCzLGZY7TtQ1PQKzvJHe	$2b$12$ol0ISZXLqII4v4kIavszJe	2025-06-02 03:07:05.250119	0	f	\N	\N	\N
7df3362d-430b-47bb-aa6d-1dbf03504fd0	azza	$2b$12$aTTcO4Bb2pbEfFyILI8CD.EdXHhQhKqUt31I68qWcgRtSDlfivfiO	$2b$12$aTTcO4Bb2pbEfFyILI8CD.	2025-06-02 03:07:06.2135	0	f	\N	\N	\N
\.


--
-- Data for Name: user_permissions; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.user_permissions (user_id, can_view_patients, can_create_patients, can_edit_patients, can_delete_patients, can_view_segmentations, can_create_segmentations, can_validate_segmentations, can_manage_appointments, can_manage_users, can_view_reports, can_export_data, custom_permissions) FROM stdin;
2b0b168e-9502-4a7e-a1e3-78dadeb769e6	t	t	t	t	t	t	t	t	t	t	t	\N
92ba5caa-db13-46ae-a9c1-fd43238fcbad	t	t	t	f	t	t	t	t	f	t	t	\N
8f48efcd-9129-4da4-bfb8-c3d0cd20b25c	t	t	t	f	t	t	t	t	f	t	t	\N
823903c2-75b0-48d1-bc7e-499f10e4c3a1	t	t	t	f	t	t	t	t	f	t	t	\N
a47bdb6a-291d-4d5e-bc37-a35104c0a70d	t	t	t	f	t	t	t	t	f	t	t	\N
7df3362d-430b-47bb-aa6d-1dbf03504fd0	t	t	t	f	t	f	f	t	f	t	f	\N
\.


--
-- Data for Name: user_sessions; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.user_sessions (session_id, user_id, created_at, expires_at, ip_address, user_agent, is_active, last_activity) FROM stdin;
urhN5c7997OrfLIGE6NMFPN4kkeB1AjHbNd-MvWf7IE	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 03:17:12.575754	2025-05-30 02:47:12.571421	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 03:17:12.575754
KqDpHQKu-HJbXRi7Nmh1olYQTHUNRh8hcLO4TVGAoAg	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 13:34:36.292457	2025-05-30 13:04:36.28623	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 13:34:36.292457
RRtu-g9Wy_Fe2VKSlacPZC8GQq-xcrfcYIlvadZPhqY	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 13:35:20.970905	2025-05-30 13:05:20.968044	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 13:35:20.970905
EAW57NAdKDCMKLpcFiQjfLpJnRXr_pioD7eJwR7HcfY	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 16:16:00.045538	2025-05-30 15:46:00.040764	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 16:16:00.045538
pCoptBOAGizpenhWWqu29pYF9SFKQo99xshIWW6Xh-E	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 16:26:40.855213	2025-05-30 15:56:40.850617	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 16:26:40.855213
1ph7kE-xgbDRBRq_R-aTUfvZ3DKgpolcc5MiIDO7JxA	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 16:56:45.942743	2025-05-30 16:26:45.93665	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 16:56:45.942743
t12FdtoGQlhRdcXM311uui5AyZZwPXLmjuP_pN9Jccs	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 17:28:37.32499	2025-05-30 16:58:37.318245	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 17:28:37.32499
g7sFgbsdHwxnAiM8I6ZTzo3LySrRP4N6euAZ0a7rGP8	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 18:51:26.515232	2025-05-30 18:21:26.499445	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 18:51:26.515232
ew_Wqr4QmNFGFsNbwySOmgU2l9U4n9MeyOMkHrW_Tvc	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 19:23:18.509972	2025-05-30 18:53:18.320674	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 19:23:18.509972
4DuTYWFiHOKM017r1rKnJyMwUV965cIFdooNTjgza3w	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 21:48:52.898525	2025-05-30 21:18:52.894767	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 21:48:52.898525
WJc6ZtdFGgIF1XVz5nSjwIBn3Iy6Ga9slHYl7w7uD4M	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 22:05:12.273278	2025-05-30 21:35:12.259991	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 22:05:12.273278
m6wMflE6cOwKd3aYlgb3DXXJSxvjXEeSBl5vMqWmyrc	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 22:36:05.687446	2025-05-30 22:06:05.68301	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 22:36:05.687446
N9pJDWh5aXCmqMccH2zK5B4aw8Ogj_UoPo0otiKGR0s	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 23:10:09.822397	2025-05-30 22:40:09.745719	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 23:10:09.822397
f1d4x9fIzXR48SyMonVTnuFtUb3DWeETmQe3NWDFlno	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-30 23:41:57.236057	2025-05-30 23:11:57.135285	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-30 23:41:57.236057
OuHYs9tx4-4dkWUyYbbGcOWaF3PRHFr1f81-eHqLFJY	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 00:13:24.885575	2025-05-30 23:43:24.677071	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 00:13:24.885575
fN7VLJdq-3u84svvyp2W_hhaOUcile2eEuNC12LY-iE	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 00:46:56.912254	2025-05-31 00:16:56.792876	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 00:46:56.912254
4LdMrPNt0Pm6CgtZOyHgiqrUJsdSqs8Wq3KluE4b3NA	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 01:23:26.5687	2025-05-31 00:53:25.252629	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 01:23:26.5687
nZQBchTbCebmnnXl5GX66tR4IbtQohHyvumfccpMSvg	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 01:49:38.363742	2025-05-31 01:19:38.360354	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 01:49:38.363742
Uvs9ImbPOrSKcuKtQ2zO5pnPdnf0KqFk_gfjewp0y0E	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 02:21:37.626836	2025-05-31 01:51:37.622908	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 02:21:37.626836
FhtARPEsEAcL3GPFUj-NASPnAiHFHcupCm9fXexr-sU	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 02:52:38.761638	2025-05-31 02:22:38.754346	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 02:52:38.761638
P3i_HW7MPEyB0MT-3coB1wt3pvcKdkPkPEdWi_W1I4o	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 03:25:41.793946	2025-05-31 02:55:41.654553	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 03:25:41.793946
Lx5pJGuPvuhyjqQMAkMP3U5rt75jYJDBR880IFAwZiY	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 04:00:30.393253	2025-05-31 03:30:30.389846	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 04:00:30.393253
YDuvM_aJIq1tMTH6G3F6mp6VWawd5u_wHFG_HE3UnEQ	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 04:32:29.577156	2025-05-31 04:02:29.571135	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 04:32:29.577156
njXhWgA9oZ24stSLtK7exunHTksmc2xQ2QAxozi9mN8	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 17:39:24.070603	2025-05-31 17:09:24.058518	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 17:39:24.070603
fgsdwoGnrFjuxUub-FRT5Eze3H9HbPg_6PyH_sYY424	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 17:44:43.102704	2025-05-31 17:14:43.099625	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 17:44:43.102704
sLXFpycRg91JmLHAYJ74D8XHtkV78hdLCBiD6mimGbM	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 18:22:25.757473	2025-05-31 17:52:25.751566	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 18:22:25.757473
jEVKw4TlmAStJwIFqdpdP6Q8lEXa21tSt2e6u9IN6UE	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 18:38:04.037692	2025-05-31 18:08:04.031078	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 18:38:04.037692
PnIudUr6rIcdmEyLPEwHIQN1PO0ZjKhQUFtCdTTtq2g	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 19:03:45.711019	2025-05-31 18:33:45.703984	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 19:03:45.711019
BYOWkeTtmVpxvDjZtYn1XTNqL48B4oJBH4EBmIaqLls	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 19:38:35.291039	2025-05-31 19:08:35.286284	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 19:38:35.291039
NXYKkvjEM81CBO_naYndVdUf7E8NA7ktpenV4Qk9T00	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 20:08:47.893688	2025-05-31 19:38:47.72528	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 20:08:47.893688
PHEIDgrQf6Uv85GrTUYyilDyBFRzVaCiX3FfenKbLw0	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 21:01:29.985081	2025-05-31 20:31:29.609204	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 21:01:29.985081
3L5vZB1mEx_nbwWAspoelC2BiloVkD7wtCeJBQs2cZw	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 22:13:36.819917	2025-05-31 21:43:36.809141	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 22:13:36.819917
vazpd5CLHz2hWF_53tiIpQl-U-Uf_mhpi8XOpSdCRyc	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 22:20:34.686209	2025-05-31 21:50:34.014059	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 22:20:34.686209
h0f64xSjwn_ZpRQs-SPznl4F44pteCpup3-56ibDPbk	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-05-31 22:20:34.701447	2025-05-31 21:50:34.691466	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-05-31 22:20:34.701447
Hs35TGOm07W-eTCh4DySNKwvzu58Z9xxJRtiZC1HH3s	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-06-01 10:40:22.568149	2025-06-01 10:10:22.563555	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-01 10:40:22.568149
8HDGpU9Biv86ShjLTsgZpSMpRQGH3rd2T4XkIVYz4VA	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-06-01 11:10:38.989858	2025-06-01 10:40:38.986424	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-01 11:10:38.989858
E5N_wHxHuh8fUdYqCjhP5wDs97M0kygPdj9k4wwBNfs	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-06-01 11:44:22.821084	2025-06-01 11:14:22.815221	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-01 11:44:22.821084
lBEcoE6Xbt4iCQa65YHC9NBOZQoo4t3PEnvuWjCBs1Y	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-06-01 12:16:43.554447	2025-06-01 19:16:43.485241	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-01 12:16:43.554447
-8EpnccCz4iXhN4djNpfNVzsDS9TOaKYisU0NupHRy4	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-06-01 13:54:37.572845	2025-06-01 20:54:37.568396	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-01 13:54:37.572845
WfshgTd592imYJ9-dr8X_v695yCalOeU-hQaKc3msDU	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-06-01 13:55:26.925706	2025-06-01 20:55:26.92267	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-01 13:55:26.925706
maSEXIicLkQBgka6aQ-56dBOPB7TT-uxtLa7NNACjIo	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-01 14:12:10.540459	2025-06-01 21:12:10.535895	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-01 14:12:10.540459
sThwzh8myA3Qdks8ae588Jf8AVrXeEJJC-FJIm0uPIg	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-01 16:19:12.881725	2025-06-01 23:19:12.873752	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-01 16:19:12.881725
WvQYwmdWwEWZ3epyBFaPrHmQrL3C3Zyah2d2aZQTIfM	a47bdb6a-291d-4d5e-bc37-a35104c0a70d	2025-06-01 16:32:37.528026	2025-06-01 23:32:37.523947	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-01 16:32:37.528026
E_B_boPBh3ExxgI0lQ2PutUWQAQNzAXLEB38Of8D1u0	a47bdb6a-291d-4d5e-bc37-a35104c0a70d	2025-06-01 16:36:50.715138	2025-06-01 23:36:50.69904	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-01 16:36:50.715138
6B-SjIonZZ4SB7D3g4aZqaaPGA5244CttjvRTfCAUZg	a47bdb6a-291d-4d5e-bc37-a35104c0a70d	2025-06-01 16:39:04.929973	2025-06-01 23:39:04.926498	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-01 16:39:04.929973
x3jAYFpJl8_U7W44OakLdBJYLgVcVwS2vkXd5ls_EBM	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 01:11:42.880286	2025-06-02 08:11:42.874007	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-02 01:11:42.880286
3qEYj6OqVX_60B38NTbLD1uGqsL2hG1yXIdq4iBGLHY	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 01:12:46.505397	2025-06-02 08:12:46.502978	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-02 01:12:46.505397
bQDpORFloMSS9TBWosPm3uDOz7TYg1bk5JYq6Hjr54U	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 02:56:33.680062	2025-06-02 09:56:33.674674	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 02:56:33.680062
fK5m1L77GgsRnqS6DtxpLV3GMaHb0dn95px6s88tfuI	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 03:00:33.232002	2025-06-02 10:00:33.22769	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 03:00:33.232002
CbY1oMj4k9YD3VPo9lh4MWB7hkuSAHGeZhMGXog0Xxw	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 03:01:49.030619	2025-06-02 10:01:49.024529	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 03:01:49.030619
psjpkFNsvdeWadxHG7WrRafzddJr3qJp3JAlFYQpjIg	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 03:03:07.110083	2025-06-02 10:03:07.108129	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 03:03:07.110083
xH2laVBNtk2FQi-nqy7rYE1POXuNo7G8LeKyU_wMcE8	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 03:06:04.330558	2025-06-02 10:06:04.324671	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 03:06:04.330558
_srsNxi65da1b2MErAeLIIHcw28PJD3fxlYeVKibPnI	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 03:19:23.65927	2025-06-02 10:19:23.648206	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 03:19:23.65927
PaEG2gAIA6NIJD0hdMqZCz8QT970LSR0rPogrbdilZU	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 03:40:03.809737	2025-06-02 10:40:03.805334	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 03:40:03.809737
b491z_-w2eLIJt5Atu69MbDpBhNMReie56I49PO4j8o	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 03:48:23.777545	2025-06-02 10:48:23.772286	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 03:48:23.777545
NDrtqt8dQfAghPEP-WbAQF-ZdALVMh_kuqPrBwIC0To	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-06-02 03:53:19.848789	2025-06-02 10:53:19.843427	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 03:53:19.848789
ET2a2deKdxUoLY08kkzXXMN1izD1PJjgWizj9G9y_NU	7df3362d-430b-47bb-aa6d-1dbf03504fd0	2025-06-02 03:53:20.942985	2025-06-02 10:53:20.939401	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 03:53:20.942985
Qe6ZvmdJs7Xn_Xd23XL7PgEPvYKYlHXH3be6JD7Pk_g	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-06-02 04:04:43.170878	2025-06-02 11:04:43.165271	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 04:04:43.170878
xhXiV1fT3XA8bhhsr1T3Js7VPyNEdJ120cwexBzj2zg	7df3362d-430b-47bb-aa6d-1dbf03504fd0	2025-06-02 04:04:43.797295	2025-06-02 11:04:43.793546	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 04:04:43.797295
QSsSh8V29tWNq9sPXm3QsgTknegY5vuVIcqtmSv2cWo	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	2025-06-02 04:07:05.329783	2025-06-02 11:07:05.32224	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 04:07:05.329783
12p2mnK5v-skrjndN7J2m2mDDEds-DHOBkEKlDANEjA	7df3362d-430b-47bb-aa6d-1dbf03504fd0	2025-06-02 04:07:06.276367	2025-06-02 11:07:06.273396	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 04:07:06.276367
3BoBFUCFaSEJqdhM8dteLL4kNyYWNV8nmmeJW6rz_HQ	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 04:07:21.364821	2025-06-02 11:07:21.362953	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-02 04:07:21.364821
rZ7jHME8GzceScflDetN0wfXA4A7CGxoaY2whTDV6I0	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 04:18:40.587972	2025-06-02 11:18:40.584421	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36	t	2025-06-02 04:18:40.587972
Ee20RFp8MGdG8gPZUrGjYNTb_u9JBRhhHnCX4MwuwIY	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 04:41:33.736047	2025-06-02 11:41:33.730079	127.0.0.1	Python/3.12 aiohttp/3.10.5	t	2025-06-02 04:41:33.736047
j4Ljg2_5jn1QqQ6YNCuNekWrpihoBJhcWdwUVXtC0I0	823903c2-75b0-48d1-bc7e-499f10e4c3a1	2025-06-02 04:43:39.868013	2025-06-02 11:43:39.85947	127.0.0.1	python-requests/2.32.3	t	2025-06-02 04:43:39.868013
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.users (id, first_name, last_name, email, phone, role, status, profile_picture, employee_id, created_at, updated_at, created_by, assigned_doctor_id) FROM stdin;
2b0b168e-9502-4a7e-a1e3-78dadeb769e6	Admin	CereBloom	admin@cerebloom.com	+1-234-567-8900	ADMIN	ACTIVE	\N	ADMIN001	2025-05-30 03:02:10.115556	2025-05-30 03:02:10.115556	\N	\N
92ba5caa-db13-46ae-a9c1-fd43238fcbad	Ahmed	ElMabrouk	ahmedelmabrouk2000@gmail.com	95075310	DOCTOR	ACTIVE	\N	DOC001	2025-05-30 19:12:55.167432	2025-05-30 19:12:55.167432	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	\N
8f48efcd-9129-4da4-bfb8-c3d0cd20b25c	Ahmed	ElMabrouk	ahmedelmabrouk@gmail.com	95075310	DOCTOR	ACTIVE	\N	DOC002	2025-05-30 19:18:24.607099	2025-05-30 19:18:24.607099	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	\N
823903c2-75b0-48d1-bc7e-499f10e4c3a1	tbib	tbib	tbib@gmail.com	\N	DOCTOR	ACTIVE	\N	DOC003	2025-06-01 14:09:36.883805	2025-06-01 14:09:36.883805	2b0b168e-9502-4a7e-a1e3-78dadeb769e6	\N
a47bdb6a-291d-4d5e-bc37-a35104c0a70d	Dr. Jean	Martin	dr.martin@cerebloom.com	+33123456789	DOCTOR	ACTIVE	\N	DOC968	2025-06-01 16:24:37.736977	2025-06-01 16:24:37.736977	\N	\N
7df3362d-430b-47bb-aa6d-1dbf03504fd0	azza	azza	azza@gmail.com	99989796	SECRETARY	ACTIVE	\N	SEC001	2025-06-01 16:47:44.080433	2025-06-01 16:47:44.080433	823903c2-75b0-48d1-bc7e-499f10e4c3a1	d12b0098-46d5-4277-9a13-0893e68779c1
\.


--
-- Data for Name: volumetric_analysis; Type: TABLE DATA; Schema: public; Owner: cerebloom_user
--

COPY public.volumetric_analysis (id, segmentation_id, total_tumor_volume, necrotic_core_volume, peritumoral_edema_volume, enhancing_tumor_volume, evolution_data, comparison_previous, tumor_burden_index, growth_rate_analysis, analysis_date) FROM stdin;
\.


--
-- Name: ai_segmentations ai_segmentations_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.ai_segmentations
    ADD CONSTRAINT ai_segmentations_pkey PRIMARY KEY (id);


--
-- Name: appointment_reminders appointment_reminders_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.appointment_reminders
    ADD CONSTRAINT appointment_reminders_pkey PRIMARY KEY (id);


--
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- Name: doctors doctors_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.doctors
    ADD CONSTRAINT doctors_pkey PRIMARY KEY (id);


--
-- Name: doctors doctors_user_id_key; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.doctors
    ADD CONSTRAINT doctors_user_id_key UNIQUE (user_id);


--
-- Name: image_series image_series_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.image_series
    ADD CONSTRAINT image_series_pkey PRIMARY KEY (id);


--
-- Name: medical_images medical_images_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.medical_images
    ADD CONSTRAINT medical_images_pkey PRIMARY KEY (id);


--
-- Name: medical_records medical_records_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_pkey PRIMARY KEY (id);


--
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (id);


--
-- Name: report_templates report_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.report_templates
    ADD CONSTRAINT report_templates_pkey PRIMARY KEY (id);


--
-- Name: secretaries secretaries_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.secretaries
    ADD CONSTRAINT secretaries_pkey PRIMARY KEY (id);


--
-- Name: secretaries secretaries_user_id_key; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.secretaries
    ADD CONSTRAINT secretaries_user_id_key UNIQUE (user_id);


--
-- Name: segmentation_comparisons segmentation_comparisons_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.segmentation_comparisons
    ADD CONSTRAINT segmentation_comparisons_pkey PRIMARY KEY (id);


--
-- Name: segmentation_reports segmentation_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.segmentation_reports
    ADD CONSTRAINT segmentation_reports_pkey PRIMARY KEY (id);


--
-- Name: treatments treatments_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.treatments
    ADD CONSTRAINT treatments_pkey PRIMARY KEY (id);


--
-- Name: tumor_segments tumor_segments_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.tumor_segments
    ADD CONSTRAINT tumor_segments_pkey PRIMARY KEY (id);


--
-- Name: user_credentials user_credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.user_credentials
    ADD CONSTRAINT user_credentials_pkey PRIMARY KEY (user_id);


--
-- Name: user_credentials user_credentials_username_key; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.user_credentials
    ADD CONSTRAINT user_credentials_username_key UNIQUE (username);


--
-- Name: user_permissions user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_pkey PRIMARY KEY (user_id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (session_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: volumetric_analysis volumetric_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.volumetric_analysis
    ADD CONSTRAINT volumetric_analysis_pkey PRIMARY KEY (id);


--
-- Name: volumetric_analysis volumetric_analysis_segmentation_id_key; Type: CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.volumetric_analysis
    ADD CONSTRAINT volumetric_analysis_segmentation_id_key UNIQUE (segmentation_id);


--
-- Name: idx_ai_segmentations_doctor_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX idx_ai_segmentations_doctor_id ON public.ai_segmentations USING btree (doctor_id);


--
-- Name: idx_ai_segmentations_image_series_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX idx_ai_segmentations_image_series_id ON public.ai_segmentations USING btree (image_series_id);


--
-- Name: idx_ai_segmentations_patient_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX idx_ai_segmentations_patient_id ON public.ai_segmentations USING btree (patient_id);


--
-- Name: idx_ai_segmentations_status; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX idx_ai_segmentations_status ON public.ai_segmentations USING btree (status);


--
-- Name: idx_users_assigned_doctor_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX idx_users_assigned_doctor_id ON public.users USING btree (assigned_doctor_id);


--
-- Name: ix_appointment_reminders_appointment_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_appointment_reminders_appointment_id ON public.appointment_reminders USING btree (appointment_id);


--
-- Name: ix_appointments_appointment_date; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_appointments_appointment_date ON public.appointments USING btree (appointment_date);


--
-- Name: ix_appointments_doctor_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_appointments_doctor_id ON public.appointments USING btree (doctor_id);


--
-- Name: ix_appointments_patient_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_appointments_patient_id ON public.appointments USING btree (patient_id);


--
-- Name: ix_appointments_status; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_appointments_status ON public.appointments USING btree (status);


--
-- Name: ix_image_series_patient_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_image_series_patient_id ON public.image_series USING btree (patient_id);


--
-- Name: ix_medical_images_modality; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_medical_images_modality ON public.medical_images USING btree (modality);


--
-- Name: ix_medical_images_patient_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_medical_images_patient_id ON public.medical_images USING btree (patient_id);


--
-- Name: ix_medical_records_doctor_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_medical_records_doctor_id ON public.medical_records USING btree (doctor_id);


--
-- Name: ix_medical_records_patient_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_medical_records_patient_id ON public.medical_records USING btree (patient_id);


--
-- Name: ix_patients_assigned_doctor_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_patients_assigned_doctor_id ON public.patients USING btree (assigned_doctor_id);


--
-- Name: ix_secretaries_assigned_doctor_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_secretaries_assigned_doctor_id ON public.secretaries USING btree (assigned_doctor_id);


--
-- Name: ix_segmentation_reports_segmentation_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_segmentation_reports_segmentation_id ON public.segmentation_reports USING btree (segmentation_id);


--
-- Name: ix_treatments_patient_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_treatments_patient_id ON public.treatments USING btree (patient_id);


--
-- Name: ix_treatments_status; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_treatments_status ON public.treatments USING btree (status);


--
-- Name: ix_tumor_segments_segment_type; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_tumor_segments_segment_type ON public.tumor_segments USING btree (segment_type);


--
-- Name: ix_tumor_segments_segmentation_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_tumor_segments_segmentation_id ON public.tumor_segments USING btree (segmentation_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_employee_id; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE UNIQUE INDEX ix_users_employee_id ON public.users USING btree (employee_id);


--
-- Name: ix_users_role; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_users_role ON public.users USING btree (role);


--
-- Name: ix_users_status; Type: INDEX; Schema: public; Owner: cerebloom_user
--

CREATE INDEX ix_users_status ON public.users USING btree (status);


--
-- Name: ai_segmentations ai_segmentations_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.ai_segmentations
    ADD CONSTRAINT ai_segmentations_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.doctors(id);


--
-- Name: ai_segmentations ai_segmentations_image_series_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.ai_segmentations
    ADD CONSTRAINT ai_segmentations_image_series_id_fkey FOREIGN KEY (image_series_id) REFERENCES public.image_series(id);


--
-- Name: ai_segmentations ai_segmentations_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.ai_segmentations
    ADD CONSTRAINT ai_segmentations_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: appointment_reminders appointment_reminders_appointment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.appointment_reminders
    ADD CONSTRAINT appointment_reminders_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES public.appointments(id);


--
-- Name: appointments appointments_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.doctors(id);


--
-- Name: appointments appointments_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: appointments appointments_previous_appointment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_previous_appointment_id_fkey FOREIGN KEY (previous_appointment_id) REFERENCES public.appointments(id);


--
-- Name: appointments appointments_scheduled_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_scheduled_by_user_id_fkey FOREIGN KEY (scheduled_by_user_id) REFERENCES public.users(id);


--
-- Name: doctors doctors_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.doctors
    ADD CONSTRAINT doctors_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users fk_users_assigned_doctor_id; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_assigned_doctor_id FOREIGN KEY (assigned_doctor_id) REFERENCES public.doctors(id) ON DELETE SET NULL;


--
-- Name: image_series image_series_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.image_series
    ADD CONSTRAINT image_series_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: medical_images medical_images_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.medical_images
    ADD CONSTRAINT medical_images_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: medical_images medical_images_uploaded_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.medical_images
    ADD CONSTRAINT medical_images_uploaded_by_user_id_fkey FOREIGN KEY (uploaded_by_user_id) REFERENCES public.users(id);


--
-- Name: medical_records medical_records_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.doctors(id);


--
-- Name: medical_records medical_records_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.medical_records
    ADD CONSTRAINT medical_records_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: patients patients_assigned_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_assigned_doctor_id_fkey FOREIGN KEY (assigned_doctor_id) REFERENCES public.doctors(id);


--
-- Name: patients patients_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: report_templates report_templates_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.report_templates
    ADD CONSTRAINT report_templates_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: secretaries secretaries_assigned_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.secretaries
    ADD CONSTRAINT secretaries_assigned_doctor_id_fkey FOREIGN KEY (assigned_doctor_id) REFERENCES public.doctors(id);


--
-- Name: secretaries secretaries_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.secretaries
    ADD CONSTRAINT secretaries_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: segmentation_reports segmentation_reports_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.segmentation_reports
    ADD CONSTRAINT segmentation_reports_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.doctors(id);


--
-- Name: segmentation_reports segmentation_reports_template_used_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.segmentation_reports
    ADD CONSTRAINT segmentation_reports_template_used_fkey FOREIGN KEY (template_used) REFERENCES public.report_templates(id);


--
-- Name: treatments treatments_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.treatments
    ADD CONSTRAINT treatments_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- Name: treatments treatments_prescribed_by_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.treatments
    ADD CONSTRAINT treatments_prescribed_by_doctor_id_fkey FOREIGN KEY (prescribed_by_doctor_id) REFERENCES public.doctors(id);


--
-- Name: user_credentials user_credentials_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.user_credentials
    ADD CONSTRAINT user_credentials_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_permissions user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_sessions user_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cerebloom_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

