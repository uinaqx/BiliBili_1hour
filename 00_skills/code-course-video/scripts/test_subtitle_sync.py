import tempfile
import pathlib
import unittest
from subtitle_sync import authored_words, captions_from_words, mapped_words, normalized_words, pause_schedule, quantize, validate


def word(text,a,b,i=0):
    return dict(text=text,start=a,end=b,token=i)


class SubtitleTimingTests(unittest.TestCase):
    def test_overlapping_sentences_merge_without_early_end(self):
        c=captions_from_words([word('上一句。',0,2),word('下一句。',1.8,4,1)],duration=4.5)
        self.assertEqual(len(c),1);self.assertEqual(c[0]['spokenEnd'],4)
        self.assertGreaterEqual(c[0]['end'],4)

    def test_pause_at_exact_boundary_is_not_added_to_previous_end(self):
        w=mapped_words([word('前句。',0,1),word('后句。',1,2,1)],[1],[.18],48000)
        self.assertEqual(w[0]['end'],1);self.assertAlmostEqual(w[1]['start'],1.18)

    def test_sample_grid_handles_float_boundary(self):
        w=mapped_words([word('R',3.49,3.8000000000000003)],[3.8],[.17],44100)
        self.assertAlmostEqual(w[0]['end'],3.8)

    def test_individual_pause_amounts_and_missing_declaration(self):
        raw=[word('早',.4,.5),word('中',.5,1,1),word('晚',1,1.5,2)]
        w=mapped_words(raw,[.5,1.],[.12,.23],48000)
        self.assertAlmostEqual(w[0]['end'],.5)
        self.assertAlmostEqual(w[1]['start'],.62)
        self.assertAlmostEqual(w[1]['end'],1.12)
        self.assertAlmostEqual(w[2]['start'],1.35)
        with self.assertRaises(ValueError):
            pause_schedule({},dict(cutsSeconds=[.5]),0,())

    def test_authored_sql_spelling_and_path_remain_whole(self):
        known=[word('sequel',0,1),word('A',1,1.2,1),word('/B.java',1.2,2,2)]
        text='SQL A/B.java。'
        mapped=authored_words(known,text,[dict(spoken='sequel',written='SQL')])
        self.assertEqual(''.join(w['text'] for w in mapped),text)
        self.assertIn('A/B.java',mapped[-1]['text'])
        self.assertEqual(mapped[-1]['end'],2)

    def test_negative_words_fold_text_without_claiming_timing(self):
        raw=normalized_words([dict(text='甲',begin_time=100,end_time=30),
                              dict(text='乙。',begin_time=300,end_time=900)])
        c=captions_from_words(raw,duration=2)
        self.assertEqual(c[0]['text'],'甲乙。')
        self.assertAlmostEqual(c[0]['start'],.3)
        self.assertAlmostEqual(c[0]['spokenEnd'],.9)

    def test_final_words_are_not_remapped_twice(self):
        w=normalized_words([dict(text='结束。',begin_time=2100,end_time=2500)])
        c=captions_from_words(w,duration=3)
        self.assertAlmostEqual(c[0]['start'],2.1);self.assertEqual(c[0]['spokenEnd'],2.5)

    def test_multi_character_word_is_indivisible(self):
        c=captions_from_words([word('这整个词不能猜字时间',0,4)],duration=5,max_chars=3)
        self.assertEqual(len(c),1);self.assertEqual(c[0]['start'],0);self.assertEqual(c[0]['spokenEnd'],4)

    def test_punctuation_owns_no_extra_time(self):
        c=captions_from_words([word('前句',0,1),word('。',1,3,1),word('后句',3,4,2)],duration=5)
        self.assertEqual(c[0]['spokenEnd'],1);self.assertAlmostEqual(c[0]['end'],1.12)
        self.assertEqual(c[1]['start'],3)

    def test_zero_time_fragment_merges(self):
        c=captions_from_words([word('甲。',0,0),word('乙。',0,1,1)],duration=2)
        self.assertEqual(len(c),1)

    def test_quantization_does_not_shorten_or_overlap(self):
        c=[dict(start=.001,end=1.004,text='甲'),dict(start=1.004,end=2.003,text='乙')]
        q=quantize(c,.01)
        self.assertEqual(q[0]['endTick'],q[1]['startTick']);self.assertGreaterEqual(q[0]['endTick']*.01,c[0]['end'])

    def test_invalid_spans_fail(self):
        with self.assertRaises(ValueError):validate([dict(start=0,end=1,spokenEnd=2,text='甲')],3)
        with self.assertRaises(ValueError):captions_from_words([word('甲',0,4)],duration=3)


if __name__=='__main__':unittest.main()
