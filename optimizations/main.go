package main

import (
	"database/sql"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"os"
	"strings"
	"time"

	_ "github.com/go-sql-driver/mysql"
	"github.com/xluohome/phonedata"
	"github.com/zerozh/ngender-go"
)

type LocationInfo struct {
	Phone     string
	PhoneType string
	Province  string
	City      string
	ZipCode   string
}

type DataInfo struct {
	Gender   string
	PhoneNum string
	Name     string
	Address  LocationInfo
}

func judgeSex(name string) string {
	gender, _ := ngender.Guess(name)

	if gender == "male" {
		return "男"
	} else {
		return "女"
	}
}

func get_location(phone_num string) LocationInfo {
	info, err := phonedata.Find(phone_num)
	if err != nil {
		log.Printf("Error getting location for phone number %s: %v", phone_num, err)
		return LocationInfo{}
	}

	return LocationInfo{
		Phone:     info.PhoneNum,
		PhoneType: info.CardType,
		Province:  info.Province,
		City:      info.City,
		ZipCode:   info.ZipCode,
	}
}

func InsertData(db *sql.DB, tableName string, dataList []DataInfo) error {
	if len(dataList) == 0 {
		return nil
	}

	// 创建SQL插入语句
	var placeholders []string
	var values []interface{}

	for _, data := range dataList {
		jsonBytes, err := json.Marshal(data.Address)
		if err != nil {
			return err
		}

		placeholders = append(placeholders, "(?, ?, ?, ?)")
		values = append(values, data.Gender, data.PhoneNum, data.Name, jsonBytes)
	}

	query := fmt.Sprintf("INSERT INTO %s (gender, phone_num, name, address) VALUES %s", tableName, strings.Join(placeholders, ","))
	stmt, err := db.Prepare(query)
	if err != nil {
		return err
	}
	defer stmt.Close()

	_, err = stmt.Exec(values...)
	if err != nil {
		return err
	}

	return nil
}

func main() {
	const batchSize = 10000
	var dataList []DataInfo

	startTime := time.Now()
	db, err := sql.Open("mysql", "root:@tcp(127.0.0.1:3306)/test")
	if err != nil {
		panic(err.Error())
	}
	defer db.Close()

	if len(os.Args) < 2 {
		log.Fatalf("Usage: ./optimization <file path>")
	}
	filePath := os.Args[1]

	file, err := os.Open(filePath)
	if err != nil {
		log.Fatalf("Error opening file: %v", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)

	// Read the header row
	_, err = reader.Read()
	if err != nil {
		log.Fatalf("Error reading CSV header: %v", err)
	}

	// Process data row by row
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Printf("Error reading CSV row: %v", err)
			continue
		}

		phone_num := record[0]
		name := record[1]

		sex := judgeSex(name)
		locationInfo := get_location(phone_num)

		data := DataInfo{
			Gender:   sex,
			PhoneNum: phone_num,
			Name:     name,
			Address:  locationInfo,
		}

		dataList = append(dataList, data)

		// 当 dataList 达到 batchSize 时进行批量插入
		if len(dataList) >= batchSize {
			err = InsertData(db, "data_info", dataList)
			if err != nil {
				log.Printf("Error inserting data: %v", err)
			}
			dataList = nil
		}
	}

	// 插入剩余数据
	if len(dataList) > 0 {
		err = InsertData(db, "data_info", dataList)
		if err != nil {
			log.Printf("Error inserting data: %v", err)
		}
	}
	elapsedTime := time.Since(startTime)
	fmt.Printf("Processing took %v\n", elapsedTime)
}
