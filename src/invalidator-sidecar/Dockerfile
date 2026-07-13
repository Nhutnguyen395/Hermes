FROM golang:1.26-alpine AS builder
WORKDIR /app
COPY go.mod ./
COPY main.go ./
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -o invalidator main.go

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/invalidator .
ENTRYPOINT ["./invalidator"]