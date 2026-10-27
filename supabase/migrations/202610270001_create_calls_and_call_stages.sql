-- Core persistence for the Cold Call Copilot.
-- Apply this migration to a new Supabase project before connecting the API.

create extension if not exists pgcrypto;

create table public.calls (
    id uuid primary key default gen_random_uuid(),
    prospect_name text,
    company_name text,
    started_at timestamptz not null default now(),
    ended_at timestamptz,
    duration_seconds integer,
    status text not null default 'in_progress',
    last_stage smallint,
    outcome text,
    original_outcome text,
    outcome_source text,
    transcript text,
    constraint calls_status_valid
        check (status in ('in_progress', 'completed')),
    constraint calls_last_stage_valid
        check (last_stage is null or last_stage between 1 and 8),
    constraint calls_duration_nonnegative
        check (duration_seconds is null or duration_seconds >= 0),
    constraint calls_outcome_valid
        check (
            outcome is null or outcome in (
                'next_step_agreed',
                'agreed_to_receive_report',
                'follow_up',
                'interested',
                'not_interested',
                'do_not_call',
                'wrong_person',
                'moved_company',
                'call_again',
                'no_answer',
                'unknown',
                'not_logged'
            )
        ),
    constraint calls_original_outcome_valid
        check (
            original_outcome is null or original_outcome in (
                'agreed_to_receive_report',
                'next_step_agreed',
                'interested',
                'follow_up',
                'call_again',
                'not_interested',
                'do_not_call',
                'wrong_person',
                'moved_company',
                'not_logged'
            )
        ),
    constraint calls_outcome_source_valid
        check (
            outcome_source is null or outcome_source in (
                'caller_selected',
                'transcript_original',
                'inferred'
            )
        ),
    constraint calls_end_not_before_start
        check (ended_at is null or ended_at >= started_at)
);

create index calls_started_at_idx on public.calls (started_at desc);
create index calls_status_started_at_idx on public.calls (status, started_at desc);

create table public.call_stages (
    id uuid primary key default gen_random_uuid(),
    call_id uuid not null references public.calls (id) on delete cascade,
    stage_number smallint not null,
    response_category text,
    prospect_words text,
    notes text,
    updated_at timestamptz not null default now(),
    constraint call_stages_stage_number_valid
        check (stage_number between 1 and 8),
    constraint call_stages_call_stage_unique
        unique (call_id, stage_number)
);

create index call_stages_call_id_idx on public.call_stages (call_id);

-- Keep updated_at current when an existing stage is edited.
create function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create trigger call_stages_set_updated_at
before update on public.call_stages
for each row
execute function public.set_updated_at();
