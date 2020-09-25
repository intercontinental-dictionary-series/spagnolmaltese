import pathlib

import pylexibank
from idspy import IDSDataset, IDSEntry


class Dataset(IDSDataset):
    dir = pathlib.Path(__file__).parent
    id = "spagnolmaltese"

    def cmd_download(self, args):
        self.raw_dir.xls2csv("ids_cl_maltese_v1.xlsx")

    def cmd_makecldf(self, args):
        glottocode = "malt1254"
        lang_id = glottocode
        lang_name = "Maltese"
        reprs = ["StandardOrth", "Phonetic"]

        args.writer.add_concepts(id_factory=lambda c: c.attributes['ids_id'])
        args.writer.add_sources(*self.raw_dir.read_bib())

        personnel = self.get_personnel(args)

        args.writer.add_language(
            ID=glottocode,
            Name="Maltese",
            Glottocode=glottocode,
            Authors=personnel['author'],
            DataEntry=personnel['data entry'],
            Consultants=personnel['consultant'],
            Representations=reprs,
            date='2020-09-17',
        )

        for form in pylexibank.progressbar(self.read_csv("ids_cl_maltese_v1.idsclldorg.csv")):
            if form.form:
                args.writer.add_lexemes(
                    Language_ID=glottocode,
                    Parameter_ID=form.ids_id,
                    Value=form.form,
                    Comment=form.comment,
                    Source="spagnol2020",
                    Transcriptions=reprs,
                    AlternativeValues=form.alt_forms,
                )

        self.apply_cldf_defaults(args)

    def entry_from_row(self, row, k):

        def parse_comment(form, org_comment):
            if '[' in form:
                r = [i.strip() for i in ''.join(form.rsplit(']', 1)).split('[', 1)]
                if r[1]:
                    comment = '[{0}]'.format(r[1])
                else:
                    comment = ''
                if org_comment:
                    return r[0], '{0} {1}'.format(org_comment, comment)
                else:
                    return r[0], comment
            else:
                return form, org_comment

        form, comment = parse_comment(row[k], row[9])

        # specific case for ';'
        if ';' in form:
            entries = []
            comments = [c.strip() for c in comment.split(',')]
            forms = [i.strip() for i in form.split(';')]
            alt_forms = [i.strip() for i in row[k+1].split(';')]
            for i, f in enumerate(forms):
                try:
                    alt_form = alt_forms[i]
                except IndexError:
                    alt_form = alt_forms[0]
                if len(comments) > 0:
                    try:
                        comment = comments[i]
                    except IndexError:
                        comment = comments[0]
                    if comment:
                        if comment[0] != '[':
                            comment = '[' + comment
                        if comment[-1] != ']':
                            comment += ']'
                else:
                    comment = ''
                entries.append(
                    IDSEntry(
                            "%s-%s" % (row[0], row[1]),
                            f,
                            alt_form,
                            comment
                        )
                )
            return entries

        # specific case for '/'
        if '/' in form:
            entries = []
            forms = [i.strip() for i in form.split(' ')]
            alt_forms = [i.strip() for i in row[k+1].split(' ')]
            if len(forms) == 2 and len(alt_forms) == 2:
                for i, f in enumerate(forms):
                    if '/' in f:
                        sf = [i.strip() for i in f.split('/')]
                        af = [i.strip() for i in alt_forms[i].split('/')]
                        if i == 0:
                            entries.append(
                                IDSEntry(
                                        "%s-%s" % (row[0], row[1]),
                                        '{0} {1}'.format(sf[0], forms[1]),
                                        '{0} {1}'.format(af[0], alt_forms[1]),
                                        comment
                                    )
                            )
                            entries.append(
                                IDSEntry(
                                        "%s-%s" % (row[0], row[1]),
                                        '{0} {1}'.format(sf[1], forms[1]),
                                        '{0} {1}'.format(af[1], alt_forms[1]),
                                        comment
                                    )
                            )
                            break
                        elif i == 1:
                            entries.append(
                                IDSEntry(
                                        "%s-%s" % (row[0], row[1]),
                                        '{0} {1}'.format(forms[0], sf[0]),
                                        '{0} {1}'.format(alt_forms[0], af[0]),
                                        comment
                                    )
                            )
                            entries.append(
                                IDSEntry(
                                        "%s-%s" % (row[0], row[1]),
                                        '{0} {1}'.format(forms[0], sf[1]),
                                        '{0} {1}'.format(alt_forms[0], af[1]),
                                        comment
                                    )
                            )
                            break
            if len(entries) != 2:
                args.log.warn("Please check {0} for balanced '/'".format(form))
            return entries

        # specific case for ','
        if ',' in form:
            entries = []
            forms = [i.strip() for i in form.split(',')]
            alt_forms = [i.strip() for i in row[k+1].split(',')]
            for i, f in enumerate(forms):
                try:
                    alt_form = alt_forms[i]
                except IndexError:
                    alt_form = alt_forms[0]
                entries.append(
                    IDSEntry(
                            "%s-%s" % (row[0], row[1]),
                            f,
                            alt_form,
                            comment
                        )
                )
            return entries

        return IDSEntry(
                        "%s-%s" % (row[0], row[1]),
                        form,
                        row[k+1],
                        comment
                    )

    def read_csv(self, fname):
        for i, row in enumerate(self.raw_dir.read_csv(fname)):
            row = [c.strip() for c in row[0:15]]
            if i > 0:
                row[0:2] = [int(float(c)) for c in row[0:2]]
                for k in [3, 5, 7, 10, 12, 14]:
                    if row[k]:
                        r = self.entry_from_row(row, k)
                        if isinstance(r, list):
                            for m in r:
                                yield m
                        else:
                            yield r
