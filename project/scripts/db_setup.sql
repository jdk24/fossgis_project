--
-- PostgreSQL database dump
--

-- Dumped from database version 11.4
-- Dumped by pg_dump version 11.4

-- Started on 2020-01-07 09:36:53

CREATE EXTENSION postgis;
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 7 (class 2615 OID 78422)
-- Name: daten; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA daten;


ALTER SCHEMA daten OWNER TO postgres;

--
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 4339 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 1454 (class 1255 OID 78441)
-- Name: luftdaten_parse(); Type: FUNCTION; Schema: daten; Owner: postgres
--

CREATE FUNCTION daten.luftdaten_parse() RETURNS void
    LANGUAGE plpgsql
    AS $$

DECLARE



  json_data jsonb;



  i jsonb;

  sid integer;



  time_stamp timestamp;

  station_id integer;

  altitude double precision;

  country varchar;

  indoor boolean;

  lon double precision;

  lat double precision;

  geom public.geometry;

 

  p10 double precision;

  p25 double precision;

 

  curr_time timestamp := date_trunc('second',now());

 

  stuttgart_clip public.geometry;

BEGIN



      

-----------------GET RAW JSON VALUES FROM INPUT TBL



  SELECT *

  FROM daten.luftdaten_raw

  INTO json_data;

 

-----------------GET BOUNDARY POLYGON 

 

 SELECT * 

 FROM public.stuttgart_stadtkreis 

 INTO stuttgart_clip;





-----------------START PARSING IN FOR LOOP WITH i AS EACH JSON ELEMENT



  FOR i in

  SELECT jsonb_array_elements(json_data)

  LOOP



-----------------WITHIN THIS SELECTION, ONLY GET SDS011 (sensorid=14) DATA



  FOR sid IN

    SELECT i->'sensor'->'sensor_type'->>'id'

    LOOP

      CASE

        WHEN sid=14 THEN 

       

		    time_stamp := (i->>'timestamp')::timestamp;

		    station_id := (i->'location'->>'id')::integer;

		    --altitude := NULLIF((i->'location'->>'altitude'),'')::double precision;

		    country := (i->'location'->>'altitude');

		    indoor := (i->'location'->>'indoor')::boolean;

		    lat := (i->'location'->>'latitude')::double precision;

		    lon := (i->'location'->>'longitude')::double precision;



		    geom := st_setsrid(st_makepoint(lon,lat),4326);

		   	   

			p10 := (i->'sensordatavalues'->0->>'value')::double precision;

			p25 := (i->'sensordatavalues'->1->>'value')::double precision;

 			

            

-----------------INSERT DATA INTO PERMANENT TBL 

            

         INSERT INTO daten.luftdaten(station_id, time_stamp, p10, p25,geom,lat)

  		 select station_id,

         time_stamp,

         p10,

         p25,

		 geom,

         lat

        -- where st_intersects(geom, st_transform(st_setsrid(stuttgart_clip,25832),4326))

  		 ON CONFLICT DO NOTHING;

        ELSE CONTINUE;

        

      END CASE;

     END LOOP;

    

END LOOP;



-----------------CREATE LOGTABLE ENTRY



INSERT INTO daten.logtable (logentry) values (('{"event":"Inserted Luftdaten data","time":"'||curr_time||'","source":"luftdaten"}')::json);



--truncate table daten.luftdaten_raw;



END;

$$;


ALTER FUNCTION daten.luftdaten_parse() OWNER TO postgres;

--
-- TOC entry 1453 (class 1255 OID 78423)
-- Name: netatmo_all(); Type: FUNCTION; Schema: daten; Owner: postgres
--

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 213 (class 1259 OID 78442)
-- Name: global_tmp; Type: TABLE; Schema: daten; Owner: postgres
--

CREATE TABLE daten.global_tmp (
    station_id integer NOT NULL,
    time_stamp timestamp without time zone NOT NULL,
    altitude double precision,
    p10 double precision,
    p25 double precision,
    geom public.geometry NOT NULL,
    idpk integer NOT NULL
);


ALTER TABLE daten.global_tmp OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 78457)
-- Name: global_tmp_idpk_seq; Type: SEQUENCE; Schema: daten; Owner: postgres
--

CREATE SEQUENCE daten.global_tmp_idpk_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE daten.global_tmp_idpk_seq OWNER TO postgres;

--
-- TOC entry 4340 (class 0 OID 0)
-- Dependencies: 216
-- Name: global_tmp_idpk_seq; Type: SEQUENCE OWNED BY; Schema: daten; Owner: postgres
--

ALTER SEQUENCE daten.global_tmp_idpk_seq OWNED BY daten.global_tmp.idpk;


--
-- TOC entry 215 (class 1259 OID 78450)
-- Name: logtable; Type: TABLE; Schema: daten; Owner: postgres
--

CREATE TABLE daten.logtable (
    pk_log integer NOT NULL,
    logentry json NOT NULL
);


ALTER TABLE daten.logtable OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 78448)
-- Name: logtable_pk_log_seq; Type: SEQUENCE; Schema: daten; Owner: postgres
--

CREATE SEQUENCE daten.logtable_pk_log_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE daten.logtable_pk_log_seq OWNER TO postgres;

--
-- TOC entry 4341 (class 0 OID 0)
-- Dependencies: 214
-- Name: logtable_pk_log_seq; Type: SEQUENCE OWNED BY; Schema: daten; Owner: postgres
--

ALTER SEQUENCE daten.logtable_pk_log_seq OWNED BY daten.logtable.pk_log;


--
-- TOC entry 220 (class 1259 OID 79600)
-- Name: luftdaten; Type: TABLE; Schema: daten; Owner: postgres
--

CREATE TABLE daten.luftdaten (
    idpk integer NOT NULL,
    station_id integer NOT NULL,
    time_stamp timestamp without time zone NOT NULL,
    p10 double precision,
    p25 double precision,
    geom public.geometry NOT NULL,
    lat double precision
);


ALTER TABLE daten.luftdaten OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 79598)
-- Name: luftdaten_idpk_seq; Type: SEQUENCE; Schema: daten; Owner: postgres
--

CREATE SEQUENCE daten.luftdaten_idpk_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE daten.luftdaten_idpk_seq OWNER TO postgres;

--
-- TOC entry 4342 (class 0 OID 0)
-- Dependencies: 219
-- Name: luftdaten_idpk_seq; Type: SEQUENCE OWNED BY; Schema: daten; Owner: postgres
--

ALTER SEQUENCE daten.luftdaten_idpk_seq OWNED BY daten.luftdaten.idpk;


--
-- TOC entry 221 (class 1259 OID 79614)
-- Name: luftdaten_raw; Type: TABLE; Schema: daten; Owner: postgres
--

CREATE TABLE daten.luftdaten_raw (
    json_data jsonb
);


ALTER TABLE daten.luftdaten_raw OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 79636)
-- Name: stuttgart_stadtkreis; Type: TABLE; Schema: daten; Owner: postgres
--

CREATE TABLE daten.stuttgart_stadtkreis (
    geom public.geometry(MultiPolygon)
);


ALTER TABLE daten.stuttgart_stadtkreis OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 78476)
-- Name: lubw_daten; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lubw_daten (
    id integer NOT NULL,
    o3_today_min_limit character varying,
    luqx_today_max_comps character varying,
    o3_yesterday_min character varying,
    no2_udolink character varying,
    o3_today_latest_ts character varying,
    o3_today_latest double precision,
    pm10_yesterday_min_class character varying,
    luqx_yesterday_max_class double precision,
    no2_yesterday_latest_limit character varying,
    pm25_yesterday_avg_limit character varying,
    pm10_h_today_max_limit character varying,
    pm10_yesterday_latest double precision,
    pm25_h_yesterday_latest double precision,
    o3_yesterday_latest_class character varying,
    no2_yesterday_max_limit character varying,
    no2_yesterday_avg_class character varying,
    o3_yesterday_avg_limit character varying,
    o3_today_max character varying,
    o3_yesterday_max_limit character varying,
    pm25_yesterday_max_class character varying,
    luqx_yesterday_max double precision,
    no2_today_latest_limit character varying,
    pm10_udolink character varying,
    pm25_today_avg character varying,
    pm10_h_today_avg_limit character varying,
    pm10_h_today_max character varying,
    rw double precision,
    o3_today_avg_class character varying,
    pm10_yesterday_min_limit character varying,
    no2_yesterday_latest_class character varying,
    pm10_yesterday_latest_class character varying,
    luqx_today_max_class double precision,
    o3_yesterday_latest_limit character varying,
    pm10_yesterday_latest_ts character varying,
    pm10_yesterday_max character varying,
    pm25_h_today_min_class character varying,
    pm25_h_yesterday_avg character varying,
    no2_yesterday_min character varying,
    o3_yesterday_latest double precision,
    hoehe double precision,
    luqx_yesterday_max_comps character varying,
    pm25_yesterday_avg_class character varying,
    o3_today_max_class character varying,
    pm10_h_today_latest double precision,
    pm10_h_today_latest_ts character varying,
    strasse character varying,
    pm25_h_today_min_limit character varying,
    pm10_h_today_latest_limit character varying,
    pm25_h_today_latest_ts character varying,
    no2_today_latest_class character varying,
    no2_yesterday_avg_limit character varying,
    pm10_today_max character varying,
    pm25_yesterday_max_limit character varying,
    today_ts character varying,
    o3_yesterday_avg character varying,
    keyattvalue character varying,
    o3_today_latest_class character varying,
    pm25_h_today_max character varying,
    o3_today_max_limit character varying,
    luqx_today_latest_class double precision,
    pm25_today_avg_class character varying,
    pm25_yesterday_max character varying,
    pm25_h_yesterday_latest_class character varying,
    no2_today_max_class character varying,
    no2_today_min character varying,
    luqx_today_latest_comps character varying,
    pm10_today_min_limit character varying,
    pm25_today_min_limit character varying,
    pm10_h_today_latest_class character varying,
    pm10_h_yesterday_avg character varying,
    pm10_h_today_min_limit character varying,
    pm10_yesterday_latest_limit character varying,
    pm25_today_latest_ts character varying,
    pm10_today_latest_ts character varying,
    pm25_h_today_max_class character varying,
    o3_today_avg_limit character varying,
    nuts character varying,
    name character varying,
    pm25_h_today_latest_limit character varying,
    pm25_today_min character varying,
    pm10_yesterday_avg_limit character varying,
    pm25_yesterday_latest double precision,
    no2_today_min_class character varying,
    pm25_h_yesterday_min_limit character varying,
    no2_today_latest character varying,
    luqx_today_latest_ts character varying,
    no2_yesterday_latest_ts character varying,
    pm25_h_yesterday_min character varying,
    no2_yesterday_avg character varying,
    pm10_yesterday_max_limit character varying,
    o3_today_min_class character varying,
    pm25_yesterday_latest_limit character varying,
    pm10_today_latest_limit character varying,
    pm25_h_yesterday_latest_ts character varying,
    o3_today_min character varying,
    o3_yesterday_avg_class character varying,
    no2_yesterday_min_limit character varying,
    pm25_h_today_avg_class character varying,
    pm25_yesterday_min_limit character varying,
    o3_yesterday_max_class character varying,
    pm10_h_yesterday_latest_limit character varying,
    ort character varying,
    pm25_yesterday_latest_ts character varying,
    pm25_h_udolink character varying,
    nuts_unit character varying,
    pm25_today_latest_limit character varying,
    type character varying,
    hw double precision,
    pm25_yesterday_latest_class character varying,
    pm10_h_yesterday_min_limit character varying,
    pm10_today_avg_limit character varying,
    no2_today_avg character varying,
    luqx_yesterday_max_ts_raw double precision,
    pm10_h_yesterday_avg_class character varying,
    no2_today_avg_limit character varying,
    pm25_h_yesterday_max_limit character varying,
    pm10_h_yesterday_min character varying,
    foto character varying,
    pm10_today_max_limit character varying,
    pm25_h_yesterday_avg_limit character varying,
    pm25_today_latest_class character varying,
    pm25_today_max_limit character varying,
    pm25_h_today_avg character varying,
    pm10_h_yesterday_latest_ts character varying,
    no2_yesterday_max character varying,
    luqx_today_latest double precision,
    pm10_today_min character varying,
    lon double precision,
    pm10_h_today_min character varying,
    no2_today_avg_class character varying,
    luqx_today_max double precision,
    pm10_today_avg_class character varying,
    o3_today_avg character varying,
    keyattname character varying,
    luqx_yesterday_max_ts character varying,
    kurzname character varying,
    o3_yesterday_max character varying,
    yesterday_ts character varying,
    pm10_yesterday_min character varying,
    pm10_h_yesterday_max_class character varying,
    pm25_h_yesterday_max_class character varying,
    pm25_yesterday_min character varying,
    no2_today_max_limit character varying,
    pm10_h_today_min_class character varying,
    pm25_today_max_class character varying,
    pm10_today_max_class character varying,
    o3_yesterday_min_class character varying,
    pm25_h_yesterday_avg_class character varying,
    pm10_today_latest double precision,
    pm25_h_today_latest double precision,
    luqx_today_max_ts_raw double precision,
    no2_today_latest_ts character varying,
    no2_today_latest_status character varying,
    pm25_today_latest double precision,
    statkenn character varying,
    pm25_h_yesterday_min_class character varying,
    pm10_yesterday_max_class character varying,
    no2_today_min_limit character varying,
    no2_yesterday_min_class character varying,
    o3_yesterday_latest_ts character varying,
    luqx_today_max_ts character varying,
    lat double precision,
    pm10_today_latest_class character varying,
    pm10_h_yesterday_latest_class character varying,
    luqx_today_latest_ts_raw double precision,
    pm10_h_yesterday_latest double precision,
    pm10_h_yesterday_max_limit character varying,
    pm25_yesterday_min_class character varying,
    pm10_h_udolink character varying,
    no2_today_max character varying,
    o3_yesterday_min_limit character varying,
    o3_udolink character varying,
    pm25_h_today_min character varying,
    aktiv character varying,
    o3_today_latest_limit character varying,
    pm10_h_today_max_class character varying,
    pm10_today_avg character varying,
    pm25_h_today_max_limit character varying,
    pm10_h_yesterday_min_class character varying,
    pm10_h_today_avg character varying,
    pm25_today_max character varying,
    pm25_h_today_avg_limit character varying,
    pm25_today_avg_limit character varying,
    publication_ts character varying,
    no2_yesterday_max_class character varying,
    pm10_h_yesterday_max character varying,
    no2_yesterday_latest double precision,
    pm10_h_yesterday_avg_limit character varying,
    pm25_h_yesterday_max character varying,
    pm10_yesterday_avg character varying,
    pm25_yesterday_avg character varying,
    pm10_today_min_class character varying,
    pm25_today_min_class character varying,
    pm10_h_today_avg_class character varying,
    pm25_h_today_latest_class character varying,
    pm10_yesterday_avg_class character varying,
    pm25_h_yesterday_latest_limit character varying,
    plz character varying,
    wkb_geometry public.geometry(Point,4326)
);


ALTER TABLE public.lubw_daten OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 78474)
-- Name: lubw_daten_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lubw_daten_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lubw_daten_id_seq OWNER TO postgres;

--
-- TOC entry 4343 (class 0 OID 0)
-- Dependencies: 217
-- Name: lubw_daten_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lubw_daten_id_seq OWNED BY public.lubw_daten.id;


--
-- TOC entry 222 (class 1259 OID 79622)
-- Name: stuttgart_stadtkreis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stuttgart_stadtkreis (
    geom public.geometry(MultiPolygon)
);


ALTER TABLE public.stuttgart_stadtkreis OWNER TO postgres;

--
-- TOC entry 4178 (class 2604 OID 78459)
-- Name: global_tmp idpk; Type: DEFAULT; Schema: daten; Owner: postgres
--

ALTER TABLE ONLY daten.global_tmp ALTER COLUMN idpk SET DEFAULT nextval('daten.global_tmp_idpk_seq'::regclass);


--
-- TOC entry 4179 (class 2604 OID 78453)
-- Name: logtable pk_log; Type: DEFAULT; Schema: daten; Owner: postgres
--

ALTER TABLE ONLY daten.logtable ALTER COLUMN pk_log SET DEFAULT nextval('daten.logtable_pk_log_seq'::regclass);


--
-- TOC entry 4181 (class 2604 OID 79603)
-- Name: luftdaten idpk; Type: DEFAULT; Schema: daten; Owner: postgres
--

ALTER TABLE ONLY daten.luftdaten ALTER COLUMN idpk SET DEFAULT nextval('daten.luftdaten_idpk_seq'::regclass);


--
-- TOC entry 4180 (class 2604 OID 78479)
-- Name: lubw_daten id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lubw_daten ALTER COLUMN id SET DEFAULT nextval('public.lubw_daten_id_seq'::regclass);


--
-- TOC entry 4323 (class 0 OID 78442)
-- Dependencies: 213
-- Data for Name: global_tmp; Type: TABLE DATA; Schema: daten; Owner: postgres
--

--
-- TOC entry 4177 (class 0 OID 77127)
-- Dependencies: 199
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys  FROM stdin;
\.


--
-- TOC entry 4332 (class 0 OID 79622)
-- Dependencies: 222
-- Data for Name: stuttgart_stadtkreis; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stuttgart_stadtkreis (geom) FROM stdin;
010600000001000000010300000001000000DF000000541006702C881F41C296948370A554410C3C6F45BD8A1F419196F4D86DA55441FF018223748D1F41DC85983A71A554413CE8E101918B1F412731D9A084A4544130B6C39077901F41F975943870A45441F0A87A450F8F1F41B9485C05F6A35441303F682A58951F41E0AC0111A9A354416045382A859C1F417A7686A5A5A354419D22C47BCD991F41996D6F8473A35441A9570ADBBF951F417223387447A3544105682229E7921F41F67928C824A354418B0F7717BD971F4196EBAB5BC8A2544141A68B6AA1961F4146C2D8807DA254414011DF10769E1F41F37A9FCC49A2544107917F87A9971F410D7AA15A9FA1544170392C9A7FA11F41FB38A15189A054413A29CFB9E3A61F411941E390ADA05441D6DF07125DA81F41C8F0CE225AA05441841E242C93AA1F41DA157A87DD9F54419074258F49A61F410B72A323CA9F54411D9A4A3F96A61F41505DD4A4A89F54410396D2C42FA81F41D93E0A06FE9E5441376F174609A91F41633FC40EA39E544104618FF2D2A71F41361475AA919E5441B0F9ED3FA99F1F418FBEFC461C9E54412BC0118046A61F41D229D1AF9C9D54416F496BF300AC1F41DD527E49F79D54419B51C6CF77AD1F4120D3C202079E5441613A4BCD5EAE1F41514BA60D0A9E544152D11E8A8FAF1F41415A9AB0079E54413495B4E9A5B01F41E6711F4B009E54418DECFAB5D1B51F417FBBD73AAA9D544184A01BF68DBC1F41350778E8F29D5441BCEEEC7789BF1F41DAD85DE1C29D5441083C1E10FBBF1F41E4E6E647809D544131325F5598CC1F4100BA805F7B9D544118D5DE0715CF1F419E13C7248F9D544136CC65C3CED11F41947D39CFA49D5441D21B4A697AD41F41D71B989F779D54413412A2A2F0DA1F41AB4245490A9D5441D0D1ED8551D41F41815E4C66A59C5441DD06F74A78D71F41A0B3CDEC839C54418DF616D48ADA1F41FFC6B72C639C54411F907E511EDB1F41C52FD55C589C544176E799447DDB1F41BEF6DD3B4F9C544187ACEF9BC1DB1F41A05B64D2419C5441DFDACC2082E21F419D717D01719C5441A4FC007E66EE1F411D8B58DD499C54417A4ABEDF27ED1F411ED2EBF8E29B5441169D23FC82E21F41C67EF746B59B5441E57F3A2EDFE11F41103A8811C19B5441269521F746DE1F419B67CB65F39B5441AE78961CB8D81F41660BC004A79B54413E20FE87FED01F41D40B71DC3C9B5441818B1D79F7C51F41DF8EA449229B5441FE90ED3168C21F41E0850561459B54410A325A9F72BE1F41FF99409A009B54413D394C50C9C01F41CCBCA624F5995441E5665BB7E1BD1F4139244B5DE69954414F0B19A0C3BA1F41B68981F1D599544149A8362A48B61F414A7AA1BF8A995441B437CBEABAB71F4168F9337A44995441C010D46270B31F4100C4D87503995441DE39BB65EFAD1F41474A8311B09854418022810F40AF1F41BB5EED4070985441BC5C89DBD7A31F41A04524D01B985441011901E5C69E1F417C5BA5E7819854417FE6E6202F9B1F415AFC813D759854414A23137785981F413DFA0726CE975441501685C842951F41BD2CB4F5A0975441F71910956C931F41949FE78087975441AAECBAF3C68F1F41CCB8B090A5975441149794E92A8F1F415915491AA1975441FCBDEC243D881F41932703606E975441B600B98C3B881F41C5010062299754411D142F2ED0811F41FA3F6DCB409754415E8AAD88047B1F41EC0646D7279754412363FC58D4781F4133C0C0E694965441078008DF207A1F41394F4DD3869654416D4A35E8A17D1F4132F2AFF8519654418EE2FF33A5801F41FA977E3516965441071C25A785831F415C0C21E7D6955441638DA673CE851F4102EB14E7A2955441BEB28AE7AA871F41C653D00370955441AD1380149E891F411A3FC3682895544151285B4F898C1F417EDD4BDFC794544156E74CD6E98F1F41FA5E1777DE94544186B653F68D921F41C5512512EA945441453879C23C951F41C377FC70ED94544120547A8792971F4156C347B3E7945441F3A66EE08D971F4131F5E1BBB99454411506ED6F84971F4194D1FA795C945441FADA1C4171971F418D2F1EF69E935441A756956BFD9C1F41EBCCF40167935441EEEF8E9D2E9E1F41EC8B25801F935441AA6B698BB59E1F416D43FDE2FF925441C8F66B5ABB7F1F41264D6F97829254415BA7E7C8EC7C1F410B07160F7C925441FEC7DE6B187A1F41837D100F7A925441E3B022209A761F41E3C13D6078925441C947864050731F41D502474B7992544195A8AE62BE6E1F413E81B5C1819254412B330153E8691F41CCDD37CC91925441064BB43811681F4186BD99D59A925441D17132DAEF641F4144F3F716B39254413777D1197A611F413328A937D2925441C09A8104F85E1F419BCC024CEA925441017D3EF9855D1F416F73A02CF8925441EAC1C84806571F41A88D45A0489354413601CA47384C1F418DAAD6E6D1935441E96053E9374A1F414ACC22BDE6935441A87D24C333481F411F1BACFCF69354418E08E7CB7F451F411D17744E089454412A99A933BD421F4130F965081694544110EC3363CE3F1F411C2D2FA823945441D2F9011BFC3C1F41DB81EDD32F945441D14BD7E120351F413AD8EA2F4B945441203E8C9888301F41E9860A955B94544172E0A954B02A1F41AE8FD46F70945441C5984A2E8C251F41E519AAD779945441761A8E9585231F41398F40717B945441E85A2975FE1F1F4155A8457D76945441B51385C671191F41D832831064945441D47744342A161F414E079D045D9454418B258C3732111F4187900DE84F945441C8FFCD28DF0D1F41D3442ABA4C94544191B82680260B1F4134EB5E3A509454413CF951C957041F41EF656B0C699454410B63646D52001F41B490DB987B94544167234F1D89FB1E41627E04FA90945441773C7C86E7F91E4154384F0399945441AC55AE081DF61E41556C7D3DAC945441CA1D751398EF1E4165321E4ECD9454418AB310DE7BEA1E417F6EF48EEB94544182EFD07F1AE71E41F9250F2608955441D43B6ABF73E41E41A3CD8654259554412CE3417AA2E11E41AD06061D4B9554417E45064DAFDB1E4152A81684A89554413F86D2FC84D81E41E286615CDA955441968BF3502BDE1E4123E6CC165496544142F190BE38DB1E41A3A1A1DF74965441F6C928C121D61E41769C2E75A3965441E84F623594CF1E41724FD84FE6965441839CE591CAD21E41B65A03993497544142A310E2ECCF1E41FEBC4BE85E97544196B890877EC51E411D474BC24E975441FEF3F3A3B0C21E41E9D7AC12E897544192F195E49EBF1E41E871F29012985441FEC36D8D0FB41E41942CD5CB11985441852930A19EB21E41223C199239985441AEDD6CE625B21E41B668EDE86C9854414245795BF8B71E410388F9BDB79854417A43A3EFB5B91E41FC660A1DCE9854417F2958D06DC01E4117B6810DDA98544129622963B9C61E41C9E4105D9D985441807C99F6F2CC1E41BE9D6124A49854415DCDD8EF17CD1E410AB4BAEA4C99544185A6E56F4ED11E41E93D8B86BF9954416566221178DA1E41D6D0E38488995441321790ADC5DB1E418FCAC871839954419B1B241C35DF1E41796D6F85DC9A5441E896B2229CE41E41EB84AA47EB9A5441D089C309A9E41E41BB9EA904DE9B54414193D7756CE91E41EBAC67CCA39C544131EF2DD8A4DB1E418FDD38CB2A9D54415A52058FBCDC1E4118E1ED4F779D5441BB43A69E7FDE1E4142582CB4F29D5441E00987EEA4E51E41AE8F8BC6379E54417C929D2BF5E51E4166F47D1F689E5441B71248D2A5E61E4140430C0BD19E544158896070DEE71E41152C08B88A9F544104BC54F8DADC1E4118D446DE10A05441ABF717044DE51E4143A8909BA9A05441CEE21FD517E61E41D1812C71D8A05441829D62B834E71E41EB712E471BA15441BDE07154A0E81E41DBEEF0EC6FA15441D3F61E1CA8E71E414801F0DBD3A15441D2D7EDD6B2E61E41BC9B560839A25441340F9E67BCE81E41741DB3F158A254413985D55B90EA1E413082B98971A25441E56C1C5859ED1E4159FC6A3193A254415891A546E6EF1E41B69C1E4658A25441D81C8DAA25F21E4150D0D94E22A254411E479C030EF81E417084CFF29AA1544152F10D14E0FF1E4149154EFEB8A1544167ECECC3A9001F41CDF4FF8151A15441EAA9DFCB91021F419E16873E3AA154410ED8471D5B061F41CD5CBBE20CA1544112B71F413F081F4169610F7CF6A05441D2DDBF47EF121F4146EA66753FA154414FD67D33681C1F41F6EC61C985A15441FD2236B0BE221F4155E5215996A1544103B0F986D2221F410F48CDF1F6A15441A725CD3DCA221F415765073E2AA254411630460BC5221F41633D39576CA25441DA8A0FB86F1C1F411A1BAD8410A35441CE8B0712D61F1F413315E10239A354416BB947B694241F416A9FA78571A35441FF7CA3231E271F415A8286BC8FA35441F94F9770D0231F410CEABEE634A4544174BF0557201E1F41F01A760C4EA454416A26A0179A1D1F413859E5DECFA4544152882A89C6251F41A6347348A9A45441099F596473261F41408139FE5EA5544106F1B68F462C1F419A16172430A55441C5035175B9341F418587F3E326A5544133EBD8AE9F381F41362FA269E2A45441324F55BA283F1F41B11E4E8B7CA454419F66E2D453441F4109C0E1FA28A454418674252278471F41054E6D601DA45441F109D39AEE491F41D529A69513A454412C02593EFC4A1F41EBE102F20FA454410E9495C3C74E1F41F3B0D68002A45441162A0FAAF34F1F41B2D8BF73FEA35441E0F741C4E8521F4157C59939F4A35441E0F09054E0591F41A171763DF5A35441CE8A3E16945E1F416150C7C4F5A3544109F7D42869721F4122B7A4B547A454411C262489B4701F4146D353E43FA5544119D807F179761F41E393FA4360A5544122F6A66A5C7D1F412E62C73FA2A554419C17AD80FE851F41C5E4468E76A55441541006702C881F41C296948370A55441
\.


--
-- TOC entry 4344 (class 0 OID 0)
-- Dependencies: 216
-- Name: global_tmp_idpk_seq; Type: SEQUENCE SET; Schema: daten; Owner: postgres
--

SELECT pg_catalog.setval('daten.global_tmp_idpk_seq', 0, true);


--
-- TOC entry 4345 (class 0 OID 0)
-- Dependencies: 214
-- Name: logtable_pk_log_seq; Type: SEQUENCE SET; Schema: daten; Owner: postgres
--

SELECT pg_catalog.setval('daten.logtable_pk_log_seq', 0, true);


--
-- TOC entry 4346 (class 0 OID 0)
-- Dependencies: 219
-- Name: luftdaten_idpk_seq; Type: SEQUENCE SET; Schema: daten; Owner: postgres
--

SELECT pg_catalog.setval('daten.luftdaten_idpk_seq', 0, true);


--
-- TOC entry 4347 (class 0 OID 0)
-- Dependencies: 217
-- Name: lubw_daten_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.lubw_daten_id_seq', 0, true);


--
-- TOC entry 4191 (class 2606 OID 79608)
-- Name: luftdaten luftdaten_pkey; Type: CONSTRAINT; Schema: daten; Owner: postgres
--

ALTER TABLE ONLY daten.luftdaten
    ADD CONSTRAINT luftdaten_pkey PRIMARY KEY (idpk);


--
-- TOC entry 4186 (class 2606 OID 78484)
-- Name: lubw_daten lubw_daten_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lubw_daten
    ADD CONSTRAINT lubw_daten_pkey PRIMARY KEY (id);


--
-- TOC entry 4182 (class 1259 OID 78467)
-- Name: geom_idx; Type: INDEX; Schema: daten; Owner: postgres
--

CREATE INDEX geom_idx ON daten.global_tmp USING gist (geom);


--
-- TOC entry 4183 (class 1259 OID 78466)
-- Name: global_tmp_idpk_idx; Type: INDEX; Schema: daten; Owner: postgres
--

CREATE INDEX global_tmp_idpk_idx ON daten.global_tmp USING btree (idpk, time_stamp);


--
-- TOC entry 4184 (class 1259 OID 78473)
-- Name: global_tmp_time_stamp_idx; Type: INDEX; Schema: daten; Owner: postgres
--

CREATE UNIQUE INDEX global_tmp_time_stamp_idx ON daten.global_tmp USING btree (time_stamp, station_id);


--
-- TOC entry 4188 (class 1259 OID 79610)
-- Name: ludftdaten_idpk_idx; Type: INDEX; Schema: daten; Owner: postgres
--

CREATE INDEX ludftdaten_idpk_idx ON daten.luftdaten USING btree (idpk, time_stamp);


--
-- TOC entry 4189 (class 1259 OID 79609)
-- Name: luftdaten_geom_idx; Type: INDEX; Schema: daten; Owner: postgres
--

CREATE INDEX luftdaten_geom_idx ON daten.luftdaten USING gist (geom);


--
-- TOC entry 4192 (class 1259 OID 79611)
-- Name: luftdaten_uq_time_station; Type: INDEX; Schema: daten; Owner: postgres
--

CREATE UNIQUE INDEX luftdaten_uq_time_station ON daten.luftdaten USING btree (time_stamp, station_id);


--
-- TOC entry 4194 (class 1259 OID 79642)
-- Name: stuttgart_stadtkreis_geom_idx; Type: INDEX; Schema: daten; Owner: postgres
--

CREATE INDEX stuttgart_stadtkreis_geom_idx ON daten.stuttgart_stadtkreis USING gist (geom);


--
-- TOC entry 4187 (class 1259 OID 78485)
-- Name: lubw_daten_wkb_geometry_geom_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX lubw_daten_wkb_geometry_geom_idx ON public.lubw_daten USING gist (wkb_geometry);


--
-- TOC entry 4193 (class 1259 OID 79631)
-- Name: stuttgart_stadtkreis_geom_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX stuttgart_stadtkreis_geom_idx ON public.stuttgart_stadtkreis USING gist (geom);


-- Completed on 2020-01-07 09:36:55

--
-- PostgreSQL database dump complete
--

