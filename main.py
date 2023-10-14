import scipdf

# article_dict = scipdf.parse_pdf_to_dict("test1.pdf")
# print(article_dict)

# xml = scipdf.parse_pdf("test1.pdf", soup=True)

scipdf.parse_figures("pdfs/test1.pdf", output_folder="out/figures")
scipdf.parse_figures("pdfs/test2.pdf", output_folder="out/figures")
