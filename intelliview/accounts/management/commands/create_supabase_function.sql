-- Function to delete all users
create or replace function delete_all_users()
returns void
language plpgsql
security definer
as $$
begin
    -- Delete from auth.users (this will cascade to other auth tables)
    delete from auth.users;
    
    -- Delete from custom_user table
    delete from public.custom_user;
    
    -- Reset sequences
    alter sequence if exists auth.users_id_seq restart with 1;
    alter sequence if exists public.custom_user_id_seq restart with 1;
end;
$$; 