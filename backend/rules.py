"""Temporal signals for human review. Never infer misconduct as a fact."""
from dataclasses import dataclass, field

THRESHOLDS = {
    'phone_visible': (0.8, 'high', 'Phone visible'),
    'phone_raised': (1.2, 'high', 'Phone raised near screen - review'),
    'no_face': (3.0, 'medium', 'No face in frame'),
    'multiple_faces': (1.0, 'high', 'More than one face'),
    'look_down': (3.0, 'medium', 'Sustained downward gaze/head pose'),
    'look_side': (3.0, 'medium', 'Sustained side gaze/head pose'),
}

@dataclass
class TemporalRules:
    since: dict = field(default_factory=dict)
    emitted: set = field(default_factory=set)
    last_timestamp: float | None = None

    def update(self, observation, now):
        # A camera stall cannot count as a sustained observation.
        if self.last_timestamp is not None and now - self.last_timestamp > 2.0:
            self.since.clear()
            self.emitted.clear()
        self.last_timestamp = now
        active = {
            'phone_visible': bool(observation.get('phones')),
            'phone_raised': any(phone.get('raised', False) for phone in observation.get('phones', [])),
            'no_face': observation.get('face_count') == 0,
            'multiple_faces': observation.get('face_count', 0) > 1,
            'look_down': observation.get('gaze') == 'down',
            'look_side': observation.get('gaze') in ('left', 'right'),
        }
        events = []
        for code, enabled in active.items():
            if not enabled:
                self.since.pop(code, None)
                self.emitted.discard(code)
                continue
            self.since.setdefault(code, now)
            threshold, severity, title = THRESHOLDS[code]
            if now - self.since[code] >= threshold and code not in self.emitted:
                self.emitted.add(code)
                events.append({'code': code, 'severity': severity, 'title': title,
                               'duration_s': round(now - self.since[code], 2),
                               'observation': observation})
        return events
