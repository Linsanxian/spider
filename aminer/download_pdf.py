import httpx
import pandas as pd


def download_pdf_from_csv(csv_path: str, pdf_url_column: str = "pdf", max_retries: int = 3) -> None:
    """
    从CSV文件中下载包含PDF文件的URL字段的PDF文件。

    Args:
        csv_path (str): 包含PDF文件URL的CSV文件的路径。
        pdf_url_column (str, optional): 包含PDF文件URL的列的名称。默认为"pdf"。
        max_retries (int, optional): 每个PDF文件下载的最大重试次数。默认为3。

    Returns:
        None
    """

    df = pd.read_csv(csv_path)
    for index, row in df.iterrows():
        name = row["id"]
        url = row[pdf_url_column]

        if pd.isna(url):
            continue

        filname = f"{name}.pdf"

        for i in range(max_retries):
            try:
                print(f"正在下载PDF文件 {url} ...")
                with httpx.stream("GET", url) as response:
                    with open(f"pdf/{filname}", "wb") as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                break
            except Exception as e:
                print(f"下载PDF文件 {url} 失败，正在进行第 {i+1} 次重试...")

    print("下载完成！")


if __name__ == "__main__":
    download_pdf_from_csv("aminer.csv")