INSERT INTO public.organizations (updated_at, created_at, id, name, slug, settings)
    VALUES (now(), now(), 1, 'ABUKI', 'default',
            '{"settings": {"beacon_consent": false}}');

INSERT INTO public.groups (id, org_id, type, name, permissions, created_at)
    VALUES (1, 1, 'builtin', 'admin', '{admin,super_admin}', now());

INSERT INTO public.groups (id, org_id, type, name, permissions, created_at)
    VALUES (2, 1, 'builtin', 'default', '{create_dashboard,create_query,edit_dashboard,edit_query,view_query,view_source,execute_query,list_users,schedule_query,list_dashboards,list_alerts,list_data_sources}',
            '2024-04-21 23:25:13.827925+00');

INSERT INTO public.users (updated_at, created_at, id, org_id, name, email, password_hash, groups,
                          api_key, details)
    VALUES (now(), now(), 1, 1, 'abuki', 'abedra42@gmail.com', 
    '$6$rounds=656000$eU6sYb5n7K.K6hZ0$tNLgO3gqYkCJnjVvdGiW7TluHeWv/3fB5J29byOmnVU66LRYuEzAoXmh/2LSRDReXdfzSg1t7pFncP03os49r0', 
    -- password: test123
            '{1,2}', 'uwgC6V8ipibQbru2Y02R4bnjqjeOLwkcQc1pSECs', format('{"active_at": "%s"}', now())::json);