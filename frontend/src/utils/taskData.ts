export interface TaskData {
    id: string;
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
    subs_generation_processing: boolean;
    voice_generation_processing: boolean;
  }