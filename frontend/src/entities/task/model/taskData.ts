export type TaskData = {
    id: string;
    number_id: number;
    title: string;
    creation_date: string;
    last_used: string;
    lang_from: string;
    lang_to: string;
    src_vid_path: string;
    src_audio_path: string;
    srt_orig_subs_path: string;
    srt_translated_subs_path: string;
    json_translated_subs_path: string;
    translated_audio_path: string;
    translated_video_path: string;
    subs_generation_status: string;
    voice_generation_status: string;
    creator_username: string;
    yt_channel: string;
    yt_name: string;
    yt_orig_url: string;
    yt_our_url: string;
}
