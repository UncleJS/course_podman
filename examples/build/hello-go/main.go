package main

import (
  "fmt"
  "log"
  "net/http"
  "os"
)

func main() {
  addr := ":8080"
  if v := os.Getenv("LISTEN_ADDR"); v != "" {
    addr = v
  }

  http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "text/plain; charset=utf-8")
    fmt.Fprintln(w, "hello from a multi-stage build")
  })

  log.Fatal(http.ListenAndServe(addr, nil))
}
