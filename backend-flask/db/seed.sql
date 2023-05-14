-- this file was manually created
INSERT INTO public.users (display_name, email, handle, cognito_user_id)
VALUES
  ('Andrew Brown','layajosh+brown@gmail.com' , 'brown' ,'02ef8f79-da34-49dc-ae29-7426af0c94f5'),
  ('Andrew Bayko','layajosh+bayko@gmail.com' , 'bayko' ,'4d40fd1d-dd82-4248-b75e-4cd4fa5611c8'),
  ('Josh L','layajosh@gmail.com' , 'josh' ,'4575c078-8d68-458e-84c7-b1dd5b042d9c');


INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'josh' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )