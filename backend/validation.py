"""Consented, metadata-only trial measurements. Never accepts or stores images."""
from collections import Counter
import math
import statistics

SCENARIOS = {
    'normal': {'title': 'Look normally at the screen', 'seconds': 60, 'required': [], 'allowed': [], 'gaze': 'center'},
    'phone': {'title': 'Show a phone clearly', 'seconds': 8, 'required': ['phone_visible'], 'allowed': ['phone_visible', 'phone_raised']},
    'raised_phone': {'title': 'Raise the phone near the screen', 'seconds': 8, 'required': ['phone_visible', 'phone_raised'], 'allowed': ['phone_visible', 'phone_raised']},
    'down': {'title': 'Look down', 'seconds': 8, 'required': ['look_down'], 'allowed': ['look_down'], 'gaze': 'down'},
    'left': {'title': 'Look to YOUR left', 'seconds': 8, 'required': ['look_side'], 'allowed': ['look_side'], 'gaze': 'left'},
    'right': {'title': 'Look to YOUR right', 'seconds': 8, 'required': ['look_side'], 'allowed': ['look_side'], 'gaze': 'right'},
    'absence': {'title': 'Leave the camera view', 'seconds': 8, 'required': ['no_face'], 'allowed': ['no_face']},
    'second_face': {'title': 'A second consenting person enters', 'seconds': 8, 'required': ['multiple_faces'], 'allowed': ['multiple_faces']},
}


class TrialBook:
    def __init__(self):
        self.trials = []

    def begin(self, scenario, now):
        if scenario not in SCENARIOS:
            raise ValueError('Unknown scenario')
        if self.trials and self.trials[-1]['state'] in ('countdown', 'measuring', 'awaiting_confirmation'):
            raise ValueError('Finish and confirm the previous trial first')
        config = SCENARIOS[scenario]
        self.trials.append({'number': len(self.trials)+1, 'scenario': scenario, 'state': 'countdown',
                            'cue_at': now+5, 'ends_at': now+5+config['seconds'], 'seconds': config['seconds'],
                            'samples': [], 'events': [], 'completed_as_instructed': None, 'notes': '',
                            'interrupted': False, 'early_signal': False})

    def tick(self, now):
        if not self.trials:
            return False
        trial = self.trials[-1]
        if trial['state'] not in ('countdown', 'measuring'):
            return False
        if now >= trial['ends_at']:
            trial['state'] = 'awaiting_confirmation'
            return True
        trial['state'] = 'measuring' if now >= trial['cue_at'] else 'countdown'
        return False

    def observe(self, observation, latency_ms, now, events):
        finished = self.tick(now)
        if not self.trials:
            return finished
        trial = self.trials[-1]
        scenario = trial['scenario']
        if trial['state'] == 'countdown' and scenario != 'normal':
            expected = SCENARIOS[scenario].get('gaze')
            early = (expected and observation.get('gaze') == expected) or \
                (scenario in ('phone', 'raised_phone') and bool(observation.get('phones'))) or \
                (scenario == 'absence' and observation.get('face_count') == 0) or \
                (scenario == 'second_face' and observation.get('face_count', 0) > 1)
            trial['early_signal'] |= bool(early)
        if trial['state'] != 'measuring':
            return finished
        # Whitelist numeric/categorical metadata. Frames, bytes and landmarks cannot enter the record.
        sample = {key: observation[key] for key in ('face_count', 'gaze', 'yaw_deg', 'pitch_deg', 'iris_dx', 'iris_dy') if key in observation}
        sample.update(t_s=round(now-trial['cue_at'], 3), processing_ms=latency_ms,
                      phone_count=len(observation.get('phones', [])),
                      raised_count=sum(bool(p.get('raised')) for p in observation.get('phones', [])))
        trial['samples'].append(sample)
        for event in events:
            trial['events'].append({'code': event['code'], 'cue_to_event_s': round(now-trial['cue_at'], 3)})
        return finished

    def interrupt(self, now):
        self.tick(now)
        if self.trials and self.trials[-1]['state'] in ('countdown', 'measuring'):
            self.trials[-1].update(state='awaiting_confirmation', interrupted=True)

    def confirm(self, completed, notes):
        if not self.trials or self.trials[-1]['state'] != 'awaiting_confirmation':
            raise ValueError('No finished trial to confirm')
        self.trials[-1].update(state='confirmed', completed_as_instructed=completed, notes=notes)

    @staticmethod
    def summary(trial):
        config = SCENARIOS[trial['scenario']]
        samples = trial['samples']
        latencies = sorted(sample['processing_ms'] for sample in samples)
        gazes = Counter(sample.get('gaze', 'unavailable') for sample in samples)
        codes = {event['code'] for event in trial['events']}
        valid = bool(trial['completed_as_instructed'] and samples and not trial['interrupted'] and not trial['early_signal'])
        return {'number': trial['number'], 'scenario': trial['scenario'], 'state': trial['state'],
                'completed_as_instructed': trial['completed_as_instructed'], 'notes': trial['notes'],
                'interrupted': trial['interrupted'], 'early_signal': trial['early_signal'],
                'assessable': valid, 'processed_frames': len(samples),
                'processing_ms_p50': round(statistics.median(latencies), 1) if latencies else None,
                'processing_ms_p95': latencies[math.ceil(.95*len(latencies))-1] if latencies else None,
                'processing_ms_max': max(latencies) if latencies else None,
                'observed_frames_per_s': round(len(samples)/trial['seconds'], 2) if not trial['interrupted'] else None,
                'gaze_counts': dict(gazes), 'face_counts': dict(Counter(str(s.get('face_count')) for s in samples)),
                'phone_frames': sum(s['phone_count'] > 0 for s in samples),
                'raised_frames': sum(s['raised_count'] > 0 for s in samples),
                'expected_gaze': config.get('gaze'),
                'expected_gaze_fraction': round(gazes[config['gaze']]/len(samples), 3) if config.get('gaze') and samples else None,
                'events': list(trial['events']),
                'missed_event_types': sorted(set(config['required'])-codes) if valid else None,
                'unexpected_event_count': sum(event['code'] not in config['allowed'] for event in trial['events']) if valid else None,
                'unexpected_event_types': sorted(codes-set(config['allowed'])) if valid else None}

    def status(self, now):
        current = self.trials[-1] if self.trials else None
        remaining = None
        if current and current['state'] in ('countdown', 'measuring'):
            boundary = current['cue_at'] if current['state'] == 'countdown' else current['ends_at']
            remaining = max(0, math.ceil(boundary-now))
        return {'current': self.summary(current) if current else None, 'remaining_s': remaining,
                'trial_count': len(self.trials)}

    def report(self):
        return {'privacy': 'Numeric/categorical metadata only; no images, video, audio or face landmarks.',
                'timing': 'Processing time is capture through JPEG encoding. Cue-to-event includes reaction and dwell time; physical action onset is not measured.',
                'direction_reference': 'Expected left/right refer to the participant, not the preview image.',
                'trials': [dict(self.summary(trial), samples=list(trial['samples'])) for trial in self.trials]}
